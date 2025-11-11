import requests
from loguru import logger
from config.settings import OPENROUTER_API_KEY, OPENROUTER_REFERER, USE_LOCAL_LLM, LOCAL_LLM_URL, LOCAL_LLM_MODEL
import time
import hashlib
import json
import os
import re

class LLMClient:
    def __init__(self):
        self.api_key = OPENROUTER_API_KEY
        self.referer = OPENROUTER_REFERER
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.last_request_time = 0
        self.rate_limit_delay = 1  # Reduced to 1 second
        self.cache_file = "llm_cache.json"
        self.cache = self._load_cache()
        
        # Local LLM configuration from settings
        self.use_local_llm = USE_LOCAL_LLM
        self.local_llm_url = LOCAL_LLM_URL
        self.local_model = LOCAL_LLM_MODEL
        
        # Multiple models for fallback (cloud-based)
        # Try models without :free suffix first, then with it if needed
        # Note: Model availability may vary. Check OpenRouter dashboard for current models
        self.models = [
            # Try common free models without :free suffix first
            "google/gemini-flash-1.5",
            "meta-llama/llama-3.2-3b-instruct",
            "microsoft/phi-3-mini-128k-instruct",
            "qwen/qwen-2.5-7b-instruct",
            # Try with :free suffix
            "google/gemini-flash-1.5:free",
            "meta-llama/llama-3.2-3b-instruct:free",
            "microsoft/phi-3-mini-128k-instruct:free",
            # Alternative free models
            "mistralai/mistral-7b-instruct",
            "mistralai/mistral-7b-instruct:free",
            "google/gemini-pro",
            "google/gemini-pro:free",
            # Fallback to paid models if free ones fail (user can use if they have credits)
            "openai/gpt-3.5-turbo",
            "anthropic/claude-3-haiku"
        ]
        self.current_model_index = 0

    def _strip_hidden_thoughts(self, text: str) -> str:
        """Remove hidden reasoning tags like <think>..</think> and similar."""
        if not text:
            return ""
        cleaned = re.sub(r"<think>[\s\S]*?</think>", "", text, flags=re.IGNORECASE)
        cleaned = re.sub(r"</?(analysis|reasoning|scratchpad)>", "", cleaned, flags=re.IGNORECASE)
        return cleaned.strip()

    def _normalize(self, text: str) -> str:
        """Normalize whitespace and strip hidden thoughts, without hard line limits."""
        if not text:
            return ""
        normalized = (
            text.replace("\r\n", "\n")
            .replace("\t", " ")
            .strip()
        )
        return normalized

    def _postprocess_answer(self, answer: str) -> str:
        """Strip hidden thoughts and normalize output without truncation."""
        return self._normalize(self._strip_hidden_thoughts(answer))

    def _load_cache(self):
        """Load response cache from file"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading cache: {str(e)}")
        return {}

    def _save_cache(self):
        """Save response cache to file"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving cache: {str(e)}")

    def _get_cache_key(self, prompt: str) -> str:
        """Generate cache key for prompt"""
        return hashlib.md5(prompt.encode()).hexdigest()

    def _get_cached_response(self, prompt: str) -> str | None:
        """Get cached response if available"""
        cache_key = self._get_cache_key(prompt)
        return self.cache.get(cache_key)

    def _cache_response(self, prompt: str, response: str):
        """Cache response for future use"""
        cache_key = self._get_cache_key(prompt)
        self.cache[cache_key] = response
        self._save_cache()

    def _try_local_llm(self, prompt: str) -> tuple[bool, str]:
        """Try local LLM using Ollama"""
        try:
            # Wrap user prompt with clear system-style instruction to avoid chain-of-thought
            instruction = (
                "You are a helpful AI assistant. Provide a clear, direct answer without hidden thoughts,"
                " analysis, or <think> tags. Provide only the final answer.\n\n"
            )
            wrapped_prompt = f"{instruction}Question: {prompt}\nAnswer:"

            payload = {
                "model": self.local_model,
                "prompt": wrapped_prompt,
                "stream": False,
                # Some Ollama models respect these options to curb verbose reasoning
                "options": {
                    "temperature": 0.3,
                    "num_predict": 600,
                    # Stop if the model starts emitting hidden-thought tags
                    "stop": ["</think>", "<think>", "<analysis>", "</analysis>"],
                }
            }
            
            response = requests.post(self.local_llm_url, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                answer = result.get("response", "").strip()
                if answer:
                    return True, self._postprocess_answer(answer)
                else:
                    return False, "empty_response"
            else:
                logger.error(f"Local LLM error: {response.status_code}")
                return False, f"error_{response.status_code}"
                
        except requests.exceptions.ConnectionError:
            logger.warning("Local LLM not available (Ollama not running)")
            return False, "connection_error"
        except Exception as e:
            logger.error(f"Local LLM exception: {str(e)}")
            return False, "exception"

    def _try_model(self, payload: dict, headers: dict) -> tuple[bool, str]:
        """Try a specific model and return success status and response"""
        try:
            response = requests.post(self.api_url, json=payload, headers=headers, timeout=30)
            self.last_request_time = time.time()
            
            if response.status_code == 200:
                result = response.json()
                answer = result["choices"][0]["message"]["content"].strip()
                return True, answer
            elif response.status_code == 429:
                logger.warning(f"Rate limited on model: {payload['model']}")
                return False, "rate_limited"
            elif response.status_code == 401:
                # Authentication error - API key issue
                error_detail = "Authentication failed. Check your OpenRouter API key."
                try:
                    error_data = response.json()
                    if "error" in error_data:
                        error_detail = error_data["error"].get("message", error_detail)
                except:
                    pass
                logger.error(f"Authentication error with model {payload['model']}: {error_detail}")
                return False, "auth_error"
            elif response.status_code == 404:
                # Model not found - try to get more details
                error_msg = "Model not found"
                try:
                    error_data = response.json()
                    if "error" in error_data:
                        error_msg = error_data["error"].get("message", error_msg)
                        logger.warning(f"Model not found: {payload['model']}. Error: {error_msg}")
                    else:
                        logger.warning(f"Model not found: {payload['model']}. This model may not be available or the name is incorrect.")
                except:
                    logger.warning(f"Model not found: {payload['model']}. This model may not be available or the name is incorrect.")
                return False, "error_404"
            else:
                # Try to get error details from response
                error_detail = f"HTTP {response.status_code}"
                try:
                    error_data = response.json()
                    if "error" in error_data:
                        error_detail = error_data["error"].get("message", error_detail)
                except:
                    pass
                logger.error(f"Error with model {payload['model']}: {error_detail}")
                return False, f"error_{response.status_code}"
                
        except requests.exceptions.Timeout:
            logger.error(f"Timeout with model {payload['model']}")
            return False, "timeout"
        except Exception as e:
            logger.error(f"Exception with model {payload['model']}: {str(e)}")
            return False, "exception"

    def generate_response(self, prompt: str) -> str:
        # Check cache first
        cached_response = self._get_cached_response(prompt)
        if cached_response:
            logger.info("Using cached response")
            return cached_response
        
        # Try local LLM first if enabled
        if self.use_local_llm:
            logger.info("Trying local LLM")
            try:
                success, result = self._try_local_llm(prompt)
                if success:
                    self._cache_response(prompt, result)
                    logger.info("Generated response using local LLM")
                    return result
                else:
                    logger.warning(f"Local LLM failed: {result}, falling back to OpenRouter cloud models")
            except Exception as e:
                logger.error(f"Local LLM exception occurred: {str(e)}, falling back to OpenRouter")
        else:
            logger.info("Local LLM disabled, using OpenRouter cloud models")
        
        # Always try OpenRouter as fallback (or primary if local LLM disabled)
        # Check if API key is configured
        if not self.api_key:
            logger.error("OpenRouter API key not configured. Cannot use cloud models.")
            return "Error: OpenRouter API key not configured. Please set OPENROUTER_API_KEY environment variable."
        
        # Minimal rate limiting for cloud models
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit_delay:
            wait_time = self.rate_limit_delay - time_since_last
            logger.info(f"Rate limiting: waiting {wait_time:.1f} seconds")
            time.sleep(wait_time)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": self.referer,
            "Content-Type": "application/json"
        }
        
        # Try multiple cloud models in sequence
        for attempt in range(len(self.models)):
            model = self.models[self.current_model_index]
            logger.info(f"Trying OpenRouter cloud model ({attempt + 1}/{len(self.models)}): {model}")
            
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": "You are a helpful AI assistant. Answer comprehensively but concisely. Do not include chain-of-thought, hidden thoughts, or <think> tags. Provide only the final answer."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 600,
                "temperature": 0.3,
                # Some providers honor stop sequences in chat completions
                "stop": ["</think>", "<think>", "<analysis>", "</analysis>"]
            }
            
            success, result = self._try_model(payload, headers)
            
            if success:
                # Cache the response
                final_answer = self._postprocess_answer(result)
                self._cache_response(prompt, final_answer)
                logger.info(f"Successfully generated response using OpenRouter model: {model}")
                return final_answer
            elif result == "rate_limited":
                logger.warning(f"Rate limited on {model}, trying next model")
                # Try next model
                self.current_model_index = (self.current_model_index + 1) % len(self.models)
                # Wait a bit longer before trying next model on rate limit
                time.sleep(2)
                continue
            else:
                logger.warning(f"Model {model} failed with: {result}, trying next model")
                # Try next model on other errors
                self.current_model_index = (self.current_model_index + 1) % len(self.models)
                continue
        
        # If all models fail, return fallback response with more details
        logger.error("All OpenRouter models failed after attempting all fallback models")
        logger.error("Please check:")
        logger.error("1. Your OpenRouter API key is correct and has credits")
        logger.error("2. The model names are correct (check OpenRouter dashboard)")
        logger.error("3. Your API key has access to the models you're trying to use")
        logger.error("4. Network connectivity is working")
        
        # Check if API key might be the issue
        if not self.api_key or self.api_key.strip() == "":
            return "Error: OpenRouter API key is not configured. Please set the OPENROUTER_API_KEY environment variable."
        
        return "Unable to generate response at this time. All OpenRouter models failed. Please check your API key configuration, ensure you have credits, and verify the models are available on OpenRouter."

    def generate_batch_responses(self, questions_with_context: list[dict]) -> list[str]:
        """Generate responses for multiple questions in a single API call"""
        # Create batch prompt
        batch_prompt = "Answer each question based on the provided context. Give concise 2-line answers only.\n\n"
        
        for i, q_data in enumerate(questions_with_context, 1):
            if q_data['has_context']:
                batch_prompt += f"Question {i}: {q_data['question']}\nContext: {q_data['context']}\n"
            else:
                batch_prompt += f"Question {i}: {q_data['question']}\nContext: General knowledge\n"
            batch_prompt += "Answer: "
            if i < len(questions_with_context):
                batch_prompt += "\n\n"
        
        # Check cache first
        cached_response = self._get_cached_response(batch_prompt)
        if cached_response:
            logger.info("Using cached batch response")
            return self._parse_batch_response(cached_response, len(questions_with_context))
        
        # Try local LLM first if enabled
        if self.use_local_llm:
            logger.info("Trying local LLM for batch processing")
            success, result = self._try_local_llm(batch_prompt)
            if success:
                self._cache_response(batch_prompt, result)
                answers = self._parse_batch_response(result, len(questions_with_context))
                logger.info("Generated batch responses using local LLM")
                return answers
            else:
                logger.warning(f"Local LLM batch processing failed: {result}, falling back to cloud models")
        
        # Minimal rate limiting for cloud models
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit_delay:
            wait_time = self.rate_limit_delay - time_since_last
            logger.info(f"Rate limiting: waiting {wait_time:.1f} seconds")
            time.sleep(wait_time)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": self.referer,
            "Content-Type": "application/json"
        }
        
        # Try multiple cloud models in sequence
        for attempt in range(len(self.models)):
            model = self.models[self.current_model_index]
            logger.info(f"Trying batch processing with cloud model: {model}")
            
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": "You are a helpful AI assistant. "},
                    {"role": "user", "content": batch_prompt}
                ],
                "max_tokens": 800,  # Increased for batch processing
                "temperature": 0.3,
                "stop": ["</think>", "<think>", "<analysis>", "</analysis>"]
            }
            
            success, result = self._try_model(payload, headers)
            
            if success:
                # Cache the response
                final_answer = self._postprocess_answer(result)
                self._cache_response(batch_prompt, final_answer)
                # Parse batch response into individual answers
                answers = self._parse_batch_response(final_answer, len(questions_with_context))
                logger.info(f"Generated batch responses using cloud model: {model}")
                return answers
            elif result == "rate_limited":
                # Try next model
                self.current_model_index = (self.current_model_index + 1) % len(self.models)
                continue
            else:
                # Try next model on other errors
                self.current_model_index = (self.current_model_index + 1) % len(self.models)
                continue
        
        # If all models fail, fallback to individual processing
        logger.warning("Batch processing failed, falling back to individual processing")
        return [self.generate_response(f"Question: {q['question']}") for q in questions_with_context]

    def _parse_batch_response(self, batch_answer: str, expected_count: int) -> list[str]:
        """Parse batch response into individual answers"""
        try:
            # Split by "Answer:" or "Question" to separate answers
            parts = batch_answer.split("Answer:")
            answers = []
            
            for part in parts[1:]:  # Skip first part (before first Answer:)
                answer = part.strip()
                if answer:
                    # Clean up the answer
                    answer = answer.split("Question")[0].strip()  # Remove any trailing question text
                    answers.append(answer)
            
            # Ensure we have the right number of answers
            while len(answers) < expected_count:
                answers.append("Unable to generate response for this question.")
            
            return answers[:expected_count]  # Return only expected number of answers
            
        except Exception as e:
            logger.error(f"Error parsing batch response: {str(e)}")
            return ["Unable to generate response for this question."] * expected_count