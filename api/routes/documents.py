from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from core.document_processor import DocumentProcessor
from core.embedding_generator import EmbeddingGenerator
from core.logger_manager import LoggerManager
from database.sqlite_client import SQLiteClient
from loguru import logger

router = APIRouter()
logger_manager = LoggerManager()

class DocumentRequest(BaseModel):
    doc_url: str

@router.post("/documents")
async def ingest_document(request: DocumentRequest):
    logger.info(f"Ingesting document: {request.doc_url}")
    try:
        processor = DocumentProcessor()
        text = processor.extract_text(request.doc_url)
        paragraphs = text.split('\n\n')
        clauses = []
        for para in paragraphs:
            sentences = para.strip().split('. ')
            clauses.extend([s.strip() + '.' for s in sentences if s.strip()])
        logger.info(f"Extracted {len(clauses)} clauses from document")
        
        max_clause_size = 40000
        chunked_clauses = []
        for clause in clauses:
            if len(clause.encode('utf-8')) > max_clause_size:
                words = clause.split()
                current_chunk = ""
                for word in words:
                    if len((current_chunk + " " + word).encode('utf-8')) > max_clause_size:
                        chunked_clauses.append(current_chunk.strip())
                        current_chunk = word
                    else:
                        current_chunk += " " + word
                if current_chunk:
                    chunked_clauses.append(current_chunk.strip())
            else:
                chunked_clauses.append(clause)
        
        sqlite = SQLiteClient()
        filename = request.doc_url.split("/")[-1]
        doc_id = sqlite.store_document(request.doc_url, filename)
        
        # Log document link
        logger_manager.log_document_link(request.doc_url, doc_id, filename)
        
        embedding_generator = EmbeddingGenerator()
        vector_ids = embedding_generator.generate_embeddings(chunked_clauses, doc_id)
        sqlite.store_clauses(doc_id, chunked_clauses, vector_ids)
        logger.info(f"Successfully ingested document, doc_id: {doc_id}")
        return {"status": "success", "doc_id": doc_id}
    except Exception as e:
        logger.error(f"Error ingesting document: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to ingest document: {str(e)}")