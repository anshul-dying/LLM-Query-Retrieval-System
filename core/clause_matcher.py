from core.embedding_generator import EmbeddingGenerator
from loguru import logger
import re

class ClauseMatcher:
    def __init__(self):
        self.embedding_generator = EmbeddingGenerator()

    def _expand_query_terms(self, query: str) -> set[str]:
        """Expand query to include related terms and variations"""
        query_lower = query.lower()
        expanded = {query_lower}
        
        # Common misspellings and variations
        expansions = {
            'prerequisit': ['prerequisite', 'prerequisites', 'requirement', 'requirements', 'pre-requisite', 'pre requisit'],
            'syllabus': ['syllabi', 'curriculum', 'course outline', 'course content', 'syllabus', 'syllabus of', 'syllabus for'],
            'operating system': ['os', 'operating systems', 'operating system', 'operating system:', 'operating system course'],
        }
        
        for term, variants in expansions.items():
            if term in query_lower:
                expanded.update(variants)
                # Also add without spaces
                expanded.add(term.replace(' ', ''))
        
        # Extract subject-specific terms (like "Operating System")
        # Pattern: "X of Y" or "Y X" where Y is a subject
        subject_patterns = [
            r'(syllabus|prerequisite|prerequisit).*?of\s+([^?]+)',
            r'(syllabus|prerequisite|prerequisit).*?for\s+([^?]+)',
        ]
        
        for pattern in subject_patterns:
            matches = re.findall(pattern, query_lower)
            for match in matches:
                if isinstance(match, tuple) and len(match) >= 2:
                    subject = match[-1].strip()
                    if subject:
                        expanded.add(subject)
                        expanded.add(f"{subject} course")
                        expanded.add(f"{subject} subject")
        
        return expanded

    def _extract_keywords(self, query: str) -> list[str]:
        """Extract important keywords from query"""
        # Remove common stop words
        stop_words = {'what', 'is', 'are', 'the', 'of', 'for', 'and', 'or', 'a', 'an', 'in', 'on', 'at', 'to', 'from'}
        words = re.findall(r'\b\w+\b', query.lower())
        keywords = [w for w in words if w not in stop_words and len(w) > 2]
        return keywords

    def _keyword_score(self, clause_text: str, query_keywords: list[str], expanded_terms: set[str]) -> float:
        """Calculate keyword matching score"""
        clause_lower = clause_text.lower()
        score = 0.0
        
        # Exact keyword matches
        for keyword in query_keywords:
            if keyword in clause_lower:
                score += 2.0  # High weight for exact matches
                # Bonus for multiple occurrences
                score += clause_lower.count(keyword) * 0.5
        
        # Expanded term matches
        for term in expanded_terms:
            if term in clause_lower:
                score += 1.0
        
        return score

    def match_clause(self, query: str, return_multiple: bool = False, doc_id: int = None) -> str | list[dict]:
        # Enhanced search with larger retrieval window
        similar_clauses = self.embedding_generator.search_similar_clauses(query, top_k=100, doc_id=doc_id)  # Increased to 100 for better recall
        
        # Extract keywords and expand terms
        query_keywords = self._extract_keywords(query)
        expanded_terms = self._expand_query_terms(query)
        
        logger.info(f"Query keywords: {query_keywords}, Expanded terms: {expanded_terms}")
        
        # Boost clauses with keyword matches
        if similar_clauses and query_keywords:
            for clause in similar_clauses:
                clause_text = clause.get("clause", "")
                keyword_score = self._keyword_score(clause_text, query_keywords, expanded_terms)
                
                # Boost semantic score with keyword score (more aggressive boosting)
                semantic_score = clause.get("score", 0)
                clause["score"] = semantic_score + (keyword_score * 1.2)  # Increased multiplier
                clause["keyword_matches"] = keyword_score > 0
        
            # Re-sort by combined score
            similar_clauses = sorted(similar_clauses, key=lambda x: x.get("score", 0), reverse=True)
        
        # Also do keyword-only search for exact matches
        if query_keywords:
            keyword_clauses = self.embedding_generator.search_by_keywords(query_keywords, doc_id=doc_id)
            # Merge keyword results with semantic results, avoiding duplicates
            seen_clauses = {c.get("clause", "")[:150] for c in similar_clauses[:30]}  # Larger dedup window
            for clause in keyword_clauses:
                clause_preview = clause.get("clause", "")[:150]
                if clause_preview not in seen_clauses:
                    # Boost keyword-only matches
                    clause["score"] = clause.get("score", 0) + 0.5
                    clause["keyword_matches"] = True
                    similar_clauses.append(clause)
                    seen_clauses.add(clause_preview)
        
        # Final sort and return more results
        similar_clauses = sorted(similar_clauses, key=lambda x: x.get("score", 0), reverse=True)[:50]  # Return top 50
        
        if not similar_clauses:
            logger.warning(f"No similar clauses found for query: {query}")
            return [] if return_multiple else ""
        
        if return_multiple:
            return similar_clauses
        return similar_clauses[0]["clause"]