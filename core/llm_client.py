import requests
from loguru import logger
from config.settings import OPENROUTER_API_KEY, OPENROUTER_REFERER, USE_LOCAL_LLM, LOCAL_LLM_URL, LOCAL_LLM_MODEL
import time
import hashlib
import json
import os

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
        self.models = [
            "moonshotai/kimi-k2:free",
            "anthropic/claude-3-haiku:free", 
            "google/gemma-3n-e2b-it:free",
            "meta-llama/llama-3.1-8b-instruct:free"
        ]
        self.current_model_index = 0

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
            payload = {
                "model": self.local_model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "num_predict": 150
                }
            }
            
            response = requests.post(self.local_llm_url, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                answer = result.get("response", "").strip()
                if answer:
                    return True, answer
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
            response = requests.post(self.api_url, json=payload, headers=headers)
            self.last_request_time = time.time()
            
            if response.status_code == 200:
                result = response.json()
                answer = result["choices"][0]["message"]["content"].strip()
                return True, answer
            elif response.status_code == 429:
                logger.warning(f"Rate limited on model: {payload['model']}")
                return False, "rate_limited"
            else:
                logger.error(f"Error with model {payload['model']}: {response.status_code}")
                return False, f"error_{response.status_code}"
                
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
            success, result = self._try_local_llm(prompt)
            if success:
                self._cache_response(prompt, result)
                logger.info("Generated response using local LLM")
                return result
            else:
                logger.warning(f"Local LLM failed: {result}, falling back to cloud models")
        
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
            logger.info(f"Trying cloud model: {model}")
            
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": "You are an insurance policy assistant. Answer questions based on the provided policy clauses. Provide direct, concise answers in 2-3 lines maximum. Do not include thinking processes, explanations, or verbose text. Give only the factual answer."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 150,
                "temperature": 0.3
            }
            
            success, result = self._try_model(payload, headers)
            
            if success:
                # Cache the response
                self._cache_response(prompt, result)
                logger.info(f"Generated response using cloud model: {model}")
                return result
            elif result == "rate_limited":
                # Try next model
                self.current_model_index = (self.current_model_index + 1) % len(self.models)
                continue
            else:
                # Try next model on other errors
                self.current_model_index = (self.current_model_index + 1) % len(self.models)
                continue
        
        # If all models fail, return fallback response
        logger.error("All models failed, returning fallback response")
        return "Unable to generate response. Please ensure Ollama is running for local LLM or try again later."

    def generate_batch_responses(self, questions_with_context: list[dict]) -> list[str]:
        """Generate responses for multiple questions in a single API call"""
        # Create batch prompt
        batch_prompt = "Answer each question based on the provided context. Give concise 2-3 line answers only.\n\n"
        
        for i, q_data in enumerate(questions_with_context, 1):
            if q_data['has_context']:
                batch_prompt += f"Question {i}: {q_data['question']}\nContext: {q_data['context']}\n"
            else:
                batch_prompt += f"Question {i}: {q_data['question']}\nContext: General insurance knowledge\n"
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
                    {"role": "system", "content": "You are an insurance policy assistant. Answer questions based on the provided context. Provide direct, concise answers in 2-3 lines maximum. Do not include thinking processes, explanations, or verbose text. Give only the factual answer."},
                    {"role": "user", "content": batch_prompt}
                ],
                "max_tokens": 800,  # Increased for batch processing
                "temperature": 0.3
            }
            
            success, result = self._try_model(payload, headers)
            
            if success:
                # Cache the response
                self._cache_response(batch_prompt, result)
                # Parse batch response into individual answers
                answers = self._parse_batch_response(result, len(questions_with_context))
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