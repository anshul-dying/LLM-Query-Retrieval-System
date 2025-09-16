import pytest
import faiss
import os
from core.embedding_generator import EmbeddingGenerator

def test_generate_embeddings():
    generator = EmbeddingGenerator()
    clauses = ["Test clause 1", "Test clause 2"]
    doc_id = 1
    vector_ids = generator.generate_embeddings(clauses, doc_id)
    assert len(vector_ids) == 2
    assert all(isinstance(vid, str) for vid in vector_ids)
    assert os.path.exists("faiss_index.bin")
    assert generator.index.ntotal == 2

def test_search_similar_clauses():
    generator = EmbeddingGenerator()
    clauses = ["Test clause about premiums", "Test clause about coverage"]
    doc_id = 2
    generator.generate_embeddings(clauses, doc_id)
    results = generator.search_similar_clauses("premiums", top_k=2)
    assert isinstance(results, list)
    assert len(results) <= 2
    assert all("clause" in res and "score" in res for res in results)