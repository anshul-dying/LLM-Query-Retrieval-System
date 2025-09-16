import pytest
from fastapi.testclient import TestClient
from api.main import app
from core.embedding_generator import EmbeddingGenerator
from database.sqlite_client import SQLiteClient

client = TestClient(app)

@pytest.mark.asyncio
async def test_process_queries():
    # Pre-populate embeddings and document
    generator = EmbeddingGenerator()
    clauses = ["A grace period of thirty days is provided for premium payment."]
    doc_id = 1
    generator.generate_embeddings(clauses, doc_id)
    sqlite = SQLiteClient()
    sqlite.store_document("https://example.com/sample.pdf", "sample.pdf")
    sqlite.store_clauses(doc_id, clauses, [f"{doc_id}_0"])
    
    response = client.post(
        "/api/v1/hackrx/run",
        json={
            "documents": "https://example.com/sample.pdf",
            "questions": ["What is the grace period for premium payment?"]
        },
        headers={"Authorization": "Bearer 790ba221b2175f79ea0d5c78c27f584946d7ed36a1b74aebe82688613a13fdc7"}
    )
    assert response.status_code == 200
    assert "answers" in response.json()
    assert len(response.json()["answers"]) == 1
    assert "thirty days" in response.json()["answers"][0].lower()