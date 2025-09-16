import pytest
from core.clause_matcher import ClauseMatcher
from core.embedding_generator import EmbeddingGenerator

def test_match_clause():
    generator = EmbeddingGenerator()
    generator.generate_embeddings(["Test clause about premiums"], doc_id=1)
    matcher = ClauseMatcher()
    result = matcher.match_clause("What is the premium payment period?")
    assert isinstance(result, str)
    result_multiple = matcher.match_clause("What is the premium payment period?", return_multiple=True)
    assert isinstance(result_multiple, list)
    assert len(result_multiple) <= 15