import os
from difflib import SequenceMatcher
from loguru import logger

class PredefinedAnswers:
    def __init__(self, file_path="Docs/query_answer.txt"):
        self.file_path = file_path
        self.predefined_qa = self._load_predefined_answers()
    
    def _load_predefined_answers(self):
        """Load predefined Q&A from text file"""
        qa_dict = {}
        try:
            if not os.path.exists(self.file_path):
                logger.warning(f"Predefined answers file not found: {self.file_path}")
                return qa_dict
            
            with open(self.file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
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
    
    def find_matching_answer(self, query: str, similarity_threshold: float = 0.8) -> str | None:
        """Find matching predefined answer for given query (ignores document name)"""
        try:
            # First try exact match
            if query in self.predefined_qa:
                logger.info(f"Found exact match for query: {query[:50]}...")
                return self.predefined_qa[query]
            
            # Try fuzzy matching
            best_match = None
            best_score = 0
            
            for stored_query, answer in self.predefined_qa.items():
                # Check query similarity
                query_similarity = SequenceMatcher(None, query.lower(), stored_query.lower()).ratio()
                
                if query_similarity > best_score and query_similarity >= similarity_threshold:
                    best_score = query_similarity
                    best_match = answer
            
            if best_match:
                logger.info(f"Found fuzzy match (score: {best_score:.2f}) for query: {query[:50]}...")
                return best_match
            
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