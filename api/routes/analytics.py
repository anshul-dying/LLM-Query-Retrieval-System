from fastapi import APIRouter, HTTPException
from core.logger_manager import LoggerManager
from core.predefined_answers import PredefinedAnswers
from loguru import logger

router = APIRouter()
logger_manager = LoggerManager()
predefined_answers = PredefinedAnswers()

@router.get("/analytics/links")
async def get_document_links():
    """Get all logged document links"""
    try:
        links = logger_manager.get_document_links()
        return {
            "status": "success",
            "count": len(links),
            "links": links
        }
    except Exception as e:
        logger.error(f"Error retrieving document links: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/queries")
async def get_all_queries():
    """Get all logged queries"""
    try:
        queries = logger_manager.get_all_queries()
        return {
            "status": "success",
            "count": len(queries),
            "queries": queries
        }
    except Exception as e:
        logger.error(f"Error retrieving queries: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/queries/{doc_id}")
async def get_queries_for_document(doc_id: int):
    """Get all queries for a specific document"""
    try:
        queries = logger_manager.get_queries_for_document(doc_id)
        return {
            "status": "success",
            "doc_id": doc_id,
            "count": len(queries),
            "queries": queries
        }
    except Exception as e:
        logger.error(f"Error retrieving queries for doc_id {doc_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/summary")
async def get_analytics_summary():
    """Get analytics summary"""
    try:
        links = logger_manager.get_document_links()
        queries = logger_manager.get_all_queries()
        
        # Get unique documents
        unique_docs = set(link['doc_id'] for link in links)
        
        # Get queries per document
        queries_per_doc = {}
        for query in queries:
            doc_id = query['doc_id']
            if doc_id not in queries_per_doc:
                queries_per_doc[doc_id] = 0
            queries_per_doc[doc_id] += 1
        
        return {
            "status": "success",
            "summary": {
                "total_documents": len(unique_docs),
                "total_queries": len(queries),
                "average_queries_per_document": len(queries) / len(unique_docs) if unique_docs else 0,
                "queries_per_document": queries_per_doc
            }
        }
    except Exception as e:
        logger.error(f"Error generating analytics summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/predefined-answers")
async def get_predefined_answers():
    """Get all predefined Q&A pairs"""
    try:
        qa_pairs = predefined_answers.get_all_predefined_qa()
        return {
            "status": "success",
            "count": len(qa_pairs),
            "predefined_answers": qa_pairs
        }
    except Exception as e:
        logger.error(f"Error retrieving predefined answers: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/predefined-answers/{doc_name}")
async def get_predefined_answers_for_document(doc_name: str):
    """Get predefined Q&A pairs for a specific document"""
    try:
        doc_qa = predefined_answers.get_qa_for_document(doc_name)
        return {
            "status": "success",
            "doc_name": doc_name,
            "count": len(doc_qa),
            "predefined_answers": doc_qa
        }
    except Exception as e:
        logger.error(f"Error retrieving predefined answers for {doc_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analytics/reload-predefined")
async def reload_predefined_answers():
    """Reload predefined answers from file"""
    try:
        predefined_answers.reload_predefined_answers()
        return {
            "status": "success",
            "message": "Predefined answers reloaded successfully"
        }
    except Exception as e:
        logger.error(f"Error reloading predefined answers: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 