from fastapi import APIRouter, HTTPException
from api.models.query import QueryRequest
from core.decision_engine import DecisionEngine
from core.document_processor import DocumentProcessor
from core.embedding_generator import EmbeddingGenerator
from core.logger_manager import LoggerManager
from database.sqlite_client import SQLiteClient
from loguru import logger

router = APIRouter()
logger_manager = LoggerManager()

@router.post("/hackrx/run")
async def process_queries(request: QueryRequest):
    try:
        # Ensure document is ingested
        processor = DocumentProcessor()
        sqlite = SQLiteClient()
        doc_id = sqlite.get_document_id(request.documents)
        extracted_text = None
        
        if not doc_id:
            logger.info(f"Ingesting document {request.documents} for query processing")
            # Use per-page extractor to preserve page numbers
            clauses_with_pages = processor.extract_clauses_with_pages(request.documents)
            clauses = [c["text"] for c in clauses_with_pages]
            pages = [c.get("page") for c in clauses_with_pages]
            max_clause_size = 40000
            chunked_clauses = []
            chunked_pages = []
            for clause_text, clause_page in zip(clauses, pages):
                if len(clause_text.encode('utf-8')) > max_clause_size:
                    words = clause_text.split()
                    current_chunk = ""
                    for word in words:
                        if len((current_chunk + " " + word).encode('utf-8')) > max_clause_size:
                            chunked_clauses.append(current_chunk.strip())
                            chunked_pages.append(clause_page)
                            current_chunk = word
                        else:
                            current_chunk += " " + word
                    if current_chunk:
                        chunked_clauses.append(current_chunk.strip())
                        chunked_pages.append(clause_page)
                else:
                    chunked_clauses.append(clause_text)
                    chunked_pages.append(clause_page)
            filename = request.documents.split("/")[-1]
            doc_id = sqlite.store_document(request.documents, filename)
            
            # Log document link
            logger_manager.log_document_link(request.documents, doc_id, filename)
            
            embedding_generator = EmbeddingGenerator()
            vector_ids = embedding_generator.generate_embeddings(chunked_clauses, doc_id, pages=chunked_pages)
            sqlite.store_clauses(doc_id, chunked_clauses, vector_ids, pages=chunked_pages)
            logger.info(f"Ingested document {request.documents}, doc_id: {doc_id}")
        else:
            # For existing documents, check if it's a secret token URL
            secret_token_url_pattern = "https://register.hackrx.in/utils/get-secret-token?hackTeam="
            if secret_token_url_pattern in request.documents:
                logger.info("Re-extracting token for existing secret token document")
                extracted_text = processor.extract_text(request.documents)

        decision_engine = DecisionEngine()
        
        # Process all questions at once, passing extracted_text and doc_name
        answers = decision_engine.process_queries(
            request.questions, 
            doc_id=doc_id, 
            doc_name=request.documents,
            extracted_text=extracted_text
        )
        
        # Log each query and response
        for i, (question, answer) in enumerate(zip(request.questions, answers)):
            logger.info(f"Processing query: {question}")
            logger_manager.log_query(request.documents, doc_id, question, answer)
        
        return {"answers": answers}
    except Exception as e:
        logger.error(f"Error processing queries: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))