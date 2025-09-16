from core.embedding_generator import EmbeddingGenerator
from loguru import logger

class ClauseMatcher:
    def __init__(self):
        self.embedding_generator = EmbeddingGenerator()

    def match_clause(self, query: str, return_multiple: bool = False, doc_id: int = None) -> str | list[dict]:
        similar_clauses = self.embedding_generator.search_similar_clauses(query, top_k=15, doc_id=doc_id)
        if not similar_clauses:
            logger.warning(f"No similar clauses found for query: {query}")
            return [] if return_multiple else ""
        if return_multiple:
            return similar_clauses
        return similar_clauses[0]["clause"]