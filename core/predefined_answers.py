import os
from difflib import SequenceMatcher
from loguru import logger
from functools import lru_cache

class PredefinedAnswers:
    def __init__(self, file_path="Docs/query_answer.txt"):
        self.file_path = file_path
        self.predefined_qa = self._load_predefined_answers()
        self._normalized_queries = {}  # Cache normalized queries for faster matching
        self._match_cache = {}  # Cache match results
        self._init_normalized_cache()
    
    def _load_predefined_answers(self):
        """Load predefined Q&A from text file"""
        qa_dict = {}
        try:
            if not os.path.exists(self.file_path):
                logger.warning(f"Predefined answers file not found: {self.file_path}")
                return qa_dict
            
            # Use readlines for better performance
            with open(self.file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for line_num, line in enumerate(lines, 1):
                    line = line.strip()
                    if line and '|' in line:
                        parts = line.split('|')
                        if len(parts) >= 3:
                            _ = parts[0].strip()
                            query = parts[1].strip()
                            answer = parts[2].strip()
                            
                            # Store by query only (ignore document name)
                            qa_dict[query] = answer
                        else:
                            logger.warning(f"Invalid format in line {line_num}: {line}")
            
            logger.info(f"Loaded {len(qa_dict)} predefined Q&A pairs")
            return qa_dict
            
        except Exception as e:
            logger.error(f"Error loading predefined answers: {str(e)}")
            return qa_dict
    
    def _init_normalized_cache(self):
        """Initialize normalized query cache for faster matching"""
        self._normalized_queries = {k.lower(): (k, v) for k, v in self.predefined_qa.items()}
    
    def find_matching_answer(self, query: str, similarity_threshold: float = 0.8) -> str | None:
        """Find matching predefined answer for given query (ignores document name) with optimizations"""
        try:
            # Check cache first
            if query in self._match_cache:
                return self._match_cache[query]
            
            query_lower = query.lower()
            
            # First try exact match (case-insensitive using normalized cache)
            if query_lower in self._normalized_queries:
                result = self._normalized_queries[query_lower][1]
                self._match_cache[query] = result
                logger.info(f"Found exact match for query: {query[:50]}...")
                return result
            
            # Try case-insensitive exact match in original dict
            if query in self.predefined_qa:
                result = self.predefined_qa[query]
                self._match_cache[query] = result
                logger.info(f"Found exact match for query: {query[:50]}...")
                return result
            
            # Try fuzzy matching with early termination optimization
            best_match = None
            best_score = 0
            query_words = set(query_lower.split())  # Extract words for faster comparison
            
            for stored_query_lower, (original_query, answer) in self._normalized_queries.items():
                # Quick word overlap check before expensive similarity calculation
                stored_words = set(stored_query_lower.split())
                word_overlap = len(query_words & stored_words) / max(len(query_words), len(stored_words))
                
                # Early skip if word overlap is too low
                if word_overlap < 0.3:
                    continue
                
                # Calculate similarity only if word overlap is promising
                query_similarity = SequenceMatcher(None, query_lower, stored_query_lower).ratio()
                
                # Early termination if we find a perfect or near-perfect match
                if query_similarity >= 0.95:
                    result = answer
                    self._match_cache[query] = result
                    logger.info(f"Found near-perfect match (score: {query_similarity:.2f}) for query: {query[:50]}...")
                    return result
                
                if query_similarity > best_score and query_similarity >= similarity_threshold:
                    best_score = query_similarity
                    best_match = answer
            
            if best_match:
                self._match_cache[query] = best_match
                logger.info(f"Found fuzzy match (score: {best_score:.2f}) for query: {query[:50]}...")
                return best_match
            
            # Cache negative result to avoid repeated searches
            self._match_cache[query] = None
            logger.info(f"No predefined answer found for query: {query[:50]}...")
            return None
            
        except Exception as e:
            logger.error(f"Error finding matching answer: {str(e)}")
            return None
    
    def get_all_predefined_qa(self) -> dict:
        """Get all predefined Q&A pairs"""
        return self.predefined_qa.copy()
    
    def get_qa_for_document(self, doc_name: str) -> dict:
        """Get all Q&A pairs for a specific document (for backward compatibility)"""
        # Since we're not using document names anymore, return all Q&A pairs
        return self.predefined_qa.copy()
    
    def reload_predefined_answers(self):
        """Reload predefined answers from file"""
        logger.info("Reloading predefined answers...")
        self.predefined_qa = self._load_predefined_answers()
        self._init_normalized_cache()  # Rebuild normalized cache
        self._match_cache.clear()  # Clear match cache 