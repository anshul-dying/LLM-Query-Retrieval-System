from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from core.document_processor import DocumentProcessor
from core.embedding_generator import EmbeddingGenerator
from core.logger_manager import LoggerManager
from core.chunking_utils import chunk_clauses_optimized
from database.sqlite_client import SQLiteClient
from loguru import logger
from fastapi import UploadFile, File
import os
import uuid

router = APIRouter()
logger_manager = LoggerManager()

class DocumentRequest(BaseModel):
    doc_url: str

@router.post("/documents")
async def ingest_document(request: DocumentRequest):
    logger.info(f"Ingesting document: {request.doc_url}")
    try:
        processor = DocumentProcessor()
        # Use new extraction with page info
        clauses_with_pages = processor.extract_clauses_with_pages(request.doc_url)
        clauses = [c["text"] for c in clauses_with_pages]
        pages = [c.get("page") for c in clauses_with_pages]
        logger.info(f"Extracted {len(clauses)} clauses (with page indices when available)")
        
        max_clause_size = 40000
        # Use optimized chunking function
        chunked_clauses, chunked_pages = chunk_clauses_optimized(clauses, pages, max_clause_size)
        logger.info(f"Prepared {len(chunked_clauses)} chunked clauses for embedding")
        
        sqlite = SQLiteClient()
        filename = request.doc_url.split("/")[-1]
        doc_id = sqlite.store_document(request.doc_url, filename)
        
        # Log document link
        logger_manager.log_document_link(request.doc_url, doc_id, filename)
        
        embedding_generator = EmbeddingGenerator()
        vector_ids = embedding_generator.generate_embeddings(chunked_clauses, doc_id, pages=chunked_pages) if len(chunked_clauses) > 0 else []
        if vector_ids:
            sqlite.store_clauses(doc_id, chunked_clauses, vector_ids, pages=chunked_pages)
        else:
            logger.warning("No clauses generated for embedding; skipping clause storage")
        logger.info(f"Successfully ingested document, doc_id: {doc_id}")
        return {"status": "success", "doc_id": doc_id}
    except Exception as e:
        logger.error(f"Error ingesting document: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to ingest document: {str(e)}")


@router.post("/documents/upload")
async def ingest_document_upload(file: UploadFile = File(...)):
    """Ingest a document provided as file upload (single page flow support)."""
    logger.info(f"Ingesting uploaded document: {file.filename}")
    try:
        processor = DocumentProcessor()

        # Save upload to temp dir
        unique_name = f"upload_{uuid.uuid4()}_{file.filename}"
        temp_path = os.path.join(processor.temp_dir, unique_name)
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Extract clauses with pages from local temp file path
        clauses_with_pages = processor.extract_clauses_with_pages(temp_path)
        clauses = [c["text"] for c in clauses_with_pages]
        pages = [c.get("page") for c in clauses_with_pages]

        max_clause_size = 40000
        # Use optimized chunking function
        chunked_clauses, chunked_pages = chunk_clauses_optimized(clauses, pages, max_clause_size)
        logger.info(f"Prepared {len(chunked_clauses)} chunked clauses for embedding (upload)")

        sqlite = SQLiteClient()
        # Store a virtual URL to key the document consistently across requests
        virtual_url = f"uploaded://{unique_name}"
        filename = file.filename
        doc_id = sqlite.store_document(virtual_url, filename)

        # Log document link (no real URL, keep virtual)
        logger_manager.log_document_link(virtual_url, doc_id, filename)

        embedding_generator = EmbeddingGenerator()
        vector_ids = embedding_generator.generate_embeddings(chunked_clauses, doc_id, pages=chunked_pages) if len(chunked_clauses) > 0 else []
        if vector_ids:
            sqlite.store_clauses(doc_id, chunked_clauses, vector_ids, pages=chunked_pages)
        else:
            logger.warning("No clauses generated for embedding (upload); skipping clause storage")

        # Cleanup temp file after processing
        try:
            os.remove(temp_path)
        except Exception:
            pass

        logger.info(f"Successfully ingested uploaded document, doc_id: {doc_id}")
        return {"status": "success", "doc_id": doc_id, "doc_url": virtual_url, "filename": filename}
    except Exception as e:
        logger.error(f"Error ingesting uploaded document: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to ingest uploaded document: {str(e)}")