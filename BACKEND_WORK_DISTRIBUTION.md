# Backend Work Distribution for Course Project Presentation

## Team of 5 Members

---

## Overview

This document outlines the backend work distribution for the LLM Query Retrieval System. Each member will be responsible for understanding, presenting, and potentially enhancing their assigned module.

---

## **Aashana: API Layer & Routes**

**Files to Master:**

- `api/main.py` - FastAPI application setup, CORS configuration
- `api/routes/documents.py` - Document ingestion endpoints
- `api/routes/queries.py` - Query processing endpoints
- `api/routes/analytics.py` - Analytics and monitoring endpoints
- `api/models/query.py` - Request/Response models

**Responsibilities:**

1. **API Architecture & Endpoints**

   - Understand FastAPI application structure
   - Document ingestion endpoints (`/api/v1/documents`, `/api/v1/documents/upload`)
   - Query processing endpoint (`/api/v1/hackrx/run`)
   - Analytics endpoints (`/api/v1/analytics/*`)
   - CORS middleware configuration

2. **Request/Response Handling**

   - Input validation using Pydantic models
   - Error handling and HTTP status codes
   - Response formatting

3. **Integration Points**
   - How routes interact with core modules
   - File upload handling
   - Async/await patterns

**Presentation Focus:**

- API endpoint structure and design
- Request/response flow
- Error handling strategies
- Integration with frontend

---

## **Aarya: Document Processing & Extraction**

**Files to Master:**

- `core/document_processor.py` - Main document processing logic
- `core/chunking_utils.py` - Text chunking utilities

**Responsibilities:**

1. **Document Processing**

   - Multi-format support (PDF, DOCX, PPTX, XLSX, ZIP, Images)
   - Text extraction from various file types
   - OCR integration for scanned documents and images
   - Page/slide number preservation

2. **Text Chunking**

   - LangChain RecursiveCharacterTextSplitter usage
   - Chunk size optimization
   - Page information preservation during chunking
   - Overlap strategies

3. **Special Cases**
   - Secret token URL handling
   - Table extraction and preservation
   - Image preprocessing for OCR
   - Binary file handling

**Presentation Focus:**

- Document processing pipeline
- Multi-format support
- OCR capabilities
- Chunking strategies and optimization

---

## **Duha: Vector Search & Embeddings**

**Files to Master:**

- `core/embedding_generator.py` - Embedding generation and FAISS operations
- `core/clause_matcher.py` - Clause matching and retrieval

**Responsibilities:**

1. **Embedding Generation**

   - SentenceTransformer model usage (`all-MiniLM-L6-v2`)
   - Batch embedding generation
   - FAISS index management
   - Metadata storage and retrieval

2. **Vector Search**

   - Semantic similarity search
   - Keyword-based search
   - Hybrid search strategies
   - Score calculation and ranking

3. **FAISS Index Operations**
   - Index creation and updates
   - Vector storage and retrieval
   - Index persistence
   - Performance optimization

**Presentation Focus:**

- Vector embeddings and semantic search
- FAISS index architecture
- Search algorithms and ranking
- Performance considerations

---

## **Anshul: Query Processing & Decision Engine**

**Files to Master:**

- `core/decision_engine.py` - Main query processing logic
- `core/predefined_answers.py` - Predefined Q&A matching

**Responsibilities:**

1. **Query Processing Pipeline**

   - Query routing and classification
   - Context retrieval and building
   - Multi-strategy clause matching
   - Query-specific scoring boosts

2. **Decision Engine Logic**

   - Predefined answer matching
   - Context building from matched clauses
   - Query type detection (CGPA, grades, syllabus, etc.)
   - Special query handling (flight numbers, secret tokens)

3. **Response Generation**
   - LLM prompt engineering
   - Query-specific instructions
   - Reference building
   - Fallback strategies

**Presentation Focus:**

- Query processing workflow
- Decision engine architecture
- Context retrieval strategies
- Response generation pipeline

---

## **Upamanyu: LLM Integration & Database**

**Files to Master:**

- `core/llm_client.py` - LLM API integration
- `database/sqlite_client.py` - Database operations
- `config/settings.py` - Configuration management

**Responsibilities:**

1. **LLM Client**

   - OpenRouter API integration
   - Local LLM support (Ollama)
   - Model fallback strategies
   - Response caching
   - Rate limiting
   - Batch processing

2. **Database Management**

   - SQLite schema and operations
   - Document storage
   - Clause storage with metadata
   - Query optimization
   - Connection pooling

3. **Configuration & Settings**
   - Environment variable management
   - API key configuration
   - Feature flags
   - System configuration

**Presentation Focus:**

- LLM integration architecture
- Database design and optimization
- Configuration management
- Caching and performance strategies

---

## **Shared Responsibilities (All Members)**

### Testing & Quality Assurance

- Each member should test their assigned module
- Integration testing between modules
- Edge case handling

### Documentation

- Code comments and docstrings
- API documentation
- Architecture diagrams

### Presentation Preparation

- Prepare slides for assigned module
- Demo preparation
- Q&A preparation

---

## **Presentation Structure Suggestion**

1. **Introduction** (Member 1) - System overview, API architecture
2. **Document Processing** (Member 2) - How documents are ingested and processed
3. **Vector Search** (Member 3) - Embeddings and similarity search
4. **Query Processing** (Member 4) - How queries are processed and answered
5. **LLM & Infrastructure** (Member 5) - LLM integration and database
6. **Demo** (All) - Live demonstration
7. **Q&A** (All) - Questions and answers

---

## **Key Integration Points to Understand**

### Flow 1: Document Ingestion

```
API Route (Member 1)
  → Document Processor (Member 2)
  → Chunking Utils (Member 2)
  → Embedding Generator (Member 3)
  → Database (Member 5)
```

### Flow 2: Query Processing

```
API Route (Member 1)
  → Decision Engine (Member 4)
  → Clause Matcher (Member 3)
  → Embedding Generator (Member 3)
  → LLM Client (Member 5)
  → Database (Member 5)
```

---

## **Quick Reference: File Ownership**

| Member   | Primary Files                                                           | Lines of Code (approx) |
| -------- | ----------------------------------------------------------------------- | ---------------------- |
| Member 1 | `api/` directory                                                        | ~250 lines             |
| Member 2 | `core/document_processor.py`, `core/chunking_utils.py`                  | ~850 lines             |
| Member 3 | `core/embedding_generator.py`, `core/clause_matcher.py`                 | ~350 lines             |
| Member 4 | `core/decision_engine.py`, `core/predefined_answers.py`                 | ~750 lines             |
| Member 5 | `core/llm_client.py`, `database/sqlite_client.py`, `config/settings.py` | ~550 lines             |

---

## **Tips for Each Member**

### Member 1 (API)

- Focus on RESTful API design principles
- Understand async/await in FastAPI
- Study error handling patterns

### Member 2 (Document Processing)

- Understand different file format parsers
- Learn about OCR technology
- Study text chunking strategies

### Member 3 (Vector Search)

- Understand vector embeddings conceptually
- Learn about FAISS indexing
- Study similarity search algorithms

### Member 4 (Query Processing)

- Understand RAG (Retrieval-Augmented Generation) pattern
- Study prompt engineering
- Learn about context window management

### Member 5 (LLM & Database)

- Understand LLM API integration
- Study database optimization techniques
- Learn about caching strategies

---

## **Questions to Prepare For**

1. How does the system handle different document formats?
2. How does semantic search work?
3. How are queries matched to relevant document sections?
4. How does the LLM generate answers?
5. How is the system optimized for performance?
6. What are the limitations of the current system?
7. How can the system be scaled?

---

## **Next Steps**

1. Each member should read and understand their assigned files
2. Run the application locally
3. Test assigned modules independently
4. Prepare presentation slides
5. Practice explaining the code flow
6. Prepare for potential questions

---

**Good luck with your presentation! 🚀**
