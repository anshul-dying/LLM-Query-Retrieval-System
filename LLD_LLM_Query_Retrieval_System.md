# Low-Level Design (LLD) - LLM Query Retrieval System

## 1. Detailed Component Design

### 1.1 API Layer Components

#### 1.1.1 FastAPI Application (`api/main.py`)
```python
from fastapi import FastAPI
from api.routes import documents, queries, analytics

app = FastAPI(
    title="LLM Query Retrieval System",
    description="AI-powered document intelligence platform",
    version="1.0.0"
)

# Middleware configuration
app.add_middleware(CORSMiddleware, allow_origins=["*"])
app.add_middleware(LoggingMiddleware)

# Route registration
app.include_router(documents.router, prefix="/api/v1", tags=["documents"])
app.include_router(queries.router, prefix="/api/v1", tags=["queries"])
app.include_router(analytics.router, prefix="/api/v1", tags=["analytics"])
```

#### 1.1.2 Query Routes (`api/routes/queries.py`)
```python
@router.post("/hackrx/run")
async def process_queries(request: QueryRequest):
    """
    Main endpoint for processing queries against documents
    """
    try:
        # 1. Document ingestion (if not already processed)
        processor = DocumentProcessor()
        doc_id = ensure_document_processed(request.documents, processor)
        
        # 2. Query processing
        decision_engine = DecisionEngine()
        answers = []
        
        for question in request.questions:
            answer = decision_engine.process_single_query(question, doc_id)
            answers.append(answer)
            
        return {"answers": answers, "doc_id": doc_id}
        
    except Exception as e:
        logger.error(f"Error processing queries: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
```

#### 1.1.3 Request/Response Models (`api/models/`)
```python
# api/models/query.py
class QueryRequest(BaseModel):
    documents: str  # Document URL or path
    questions: List[str]  # List of questions to process
    
    class Config:
        schema_extra = {
            "example": {
                "documents": "https://example.com/policy.pdf",
                "questions": ["What is the coverage limit?", "What are the exclusions?"]
            }
        }

class QueryResponse(BaseModel):
    answers: List[str]
    doc_id: int
    processing_time: float
    cache_hit: bool
```

### 1.2 Business Logic Layer Components

#### 1.2.1 Decision Engine (`core/decision_engine.py`)
```python
class DecisionEngine:
    def __init__(self):
        self.clause_matcher = ClauseMatcher()
        self.llm_client = LLMClient()
        self.cache_manager = CacheManager()
        self.logger_manager = LoggerManager()
    
    def process_single_query(self, query: str, doc_id: int) -> str:
        """
        Process a single query through the complete pipeline
        """
        # 1. Check cache first
        cached_response = self.cache_manager.get_cached_response(query, doc_id)
        if cached_response:
            self.logger_manager.log_cache_hit(query, doc_id)
            return cached_response
        
        # 2. Perform semantic search
        matched_clauses = self.clause_matcher.match_clause(
            query, return_multiple=True, doc_id=doc_id
        )
        
        # 3. Generate response
        if matched_clauses:
            context = self._assemble_context(matched_clauses)
            response = self.llm_client.generate_response(query, context)
        else:
            response = self._generate_fallback_response(query)
        
        # 4. Cache response
        self.cache_manager.cache_response(query, doc_id, response)
        
        # 5. Log query
        self.logger_manager.log_query(query, doc_id, response)
        
        return response
    
    def _assemble_context(self, matched_clauses: List[dict]) -> str:
        """Assemble context from matched clauses"""
        context_parts = []
        for clause in matched_clauses[:3]:  # Top 3 most relevant
            context_parts.append(clause["clause"])
        return "\n\n".join(context_parts)
    
    def _generate_fallback_response(self, query: str) -> str:
        """Generate fallback response when no context is found"""
        prompt = f"Question: {query}\n\nAnswer based on general insurance knowledge:"
        return self.llm_client.generate_response(prompt)
```

#### 1.2.2 Document Processor (`core/document_processor.py`)
```python
class DocumentProcessor:
    def __init__(self):
        self.temp_dir = TEMP_DIR
        self.supported_formats = {
            '.pdf': self._extract_pdf,
            '.docx': self._extract_docx,
            '.pptx': self._extract_powerpoint,
            '.xlsx': self._extract_excel,
            '.jpg': self._extract_image,
            '.png': self._extract_image,
            '.zip': self._extract_zip
        }
    
    def extract_text(self, doc_url: str) -> str:
        """Main entry point for document text extraction"""
        file_extension = self._get_file_extension(doc_url)
        
        if file_extension not in self.supported_formats:
            raise ValueError(f"Unsupported file format: {file_extension}")
        
        extractor = self.supported_formats[file_extension]
        return extractor(doc_url)
    
    def _extract_pdf(self, doc_url: str) -> str:
        """Extract text from PDF files"""
        temp_file = self._download_file(doc_url, '.pdf')
        try:
            with open(temp_file, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text.strip()
        finally:
            self._safe_remove_file(temp_file)
    
    def _chunk_text(self, text: str, max_chunk_size: int = 40000) -> List[str]:
        """Split text into manageable chunks"""
        paragraphs = text.split('\n\n')
        chunks = []
        
        for para in paragraphs:
            if len(para.encode('utf-8')) > max_chunk_size:
                # Split large paragraphs
                sentences = para.split('. ')
                current_chunk = ""
                
                for sentence in sentences:
                    if len((current_chunk + " " + sentence).encode('utf-8')) > max_chunk_size:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                        current_chunk = sentence
                    else:
                        current_chunk += " " + sentence
                
                if current_chunk:
                    chunks.append(current_chunk.strip())
            else:
                chunks.append(para.strip())
        
        return [chunk for chunk in chunks if chunk]
```

#### 1.2.3 Embedding Generator (`core/embedding_generator.py`)
```python
class EmbeddingGenerator:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.dimension = 384
        self.index_path = "faiss_index.bin"
        self.metadata_path = "clause_metadata.json"
        self.index = self._load_or_create_index()
        self.clause_metadata = self._load_metadata()
    
    def generate_embeddings(self, clauses: List[str], doc_id: int) -> List[str]:
        """Generate embeddings for document clauses"""
        try:
            # Generate embeddings in batches
            embeddings = self.model.encode(
                clauses, 
                show_progress_bar=False, 
                batch_size=16
            )
            
            vector_ids = []
            for i, (clause, embedding) in enumerate(zip(clauses, embeddings)):
                vector_id = f"{doc_id}_{i}"
                
                # Add to FAISS index
                self.index.add(np.array([embedding]).astype('float32'))
                
                # Store metadata
                self.clause_metadata[vector_id] = {
                    "clause": clause,
                    "doc_id": doc_id,
                    "created_at": datetime.now().isoformat()
                }
                
                vector_ids.append(vector_id)
            
            # Persist changes
            self._save_index()
            self._save_metadata()
            
            return vector_ids
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise
    
    def search_similar_clauses(self, query: str, top_k: int = 30, doc_id: int = None) -> List[dict]:
        """Search for similar clauses using semantic similarity"""
        try:
            # Generate query embedding
            query_embedding = self.model.encode([query])[0].astype('float32')
            
            # Search in FAISS index
            distances, indices = self.index.search(
                np.array([query_embedding]), 
                top_k
            )
            
            results = []
            metadata_keys = list(self.clause_metadata.keys())
            
            for idx, distance in zip(indices[0], distances[0]):
                if idx != -1 and idx < len(metadata_keys):
                    vector_id = metadata_keys[idx]
                    clause_data = self.clause_metadata[vector_id]
                    
                    # Filter by document ID if specified
                    if doc_id is not None and clause_data["doc_id"] != doc_id:
                        continue
                    
                    # Calculate similarity score
                    score = 1 / (1 + distance)
                    
                    # Apply threshold
                    if score > 0.05:
                        results.append({
                            "clause": clause_data["clause"],
                            "score": float(score),
                            "vector_id": vector_id
                        })
            
            # Sort by score (highest first)
            results.sort(key=lambda x: x["score"], reverse=True)
            return results
            
        except Exception as e:
            logger.error(f"Error searching similar clauses: {str(e)}")
            return []
```

#### 1.2.4 LLM Client (`core/llm_client.py`)
```python
class LLMClient:
    def __init__(self):
        self.api_key = OPENROUTER_API_KEY
        self.referer = OPENROUTER_REFERER
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.use_local_llm = USE_LOCAL_LLM
        self.local_llm_url = LOCAL_LLM_URL
        self.local_model = LOCAL_LLM_MODEL
        
        # Cloud models for fallback
        self.cloud_models = [
            "moonshotai/kimi-k2:free",
            "anthropic/claude-3-haiku:free",
            "google/gemma-3n-e2b-it:free",
            "meta-llama/llama-3.1-8b-instruct:free"
        ]
        self.current_model_index = 0
        
        # Rate limiting
        self.last_request_time = 0
        self.rate_limit_delay = 1
    
    def generate_response(self, prompt: str, context: str = None) -> str:
        """Generate response using LLM"""
        try:
            # Check cache first
            cache_key = self._get_cache_key(prompt, context)
            cached_response = self._get_cached_response(cache_key)
            if cached_response:
                return cached_response
            
            # Prepare prompt with context
            full_prompt = self._prepare_prompt(prompt, context)
            
            # Try local LLM first
            if self.use_local_llm:
                success, response = self._try_local_llm(full_prompt)
                if success:
                    self._cache_response(cache_key, response)
                    return response
            
            # Fallback to cloud LLM
            response = self._try_cloud_llm(full_prompt)
            if response:
                self._cache_response(cache_key, response)
                return response
            
            return "Unable to generate response at this time."
            
        except Exception as e:
            logger.error(f"Error generating LLM response: {str(e)}")
            return "Error generating response."
    
    def _prepare_prompt(self, prompt: str, context: str = None) -> str:
        """Prepare prompt with context for LLM"""
        if context:
            return f"""Context from insurance policy:
{context}

Question: {prompt}

Please provide a clear, accurate answer based on the context above. If the context doesn't contain relevant information, provide a general insurance-related response."""
        else:
            return f"Question: {prompt}\n\nAnswer based on general insurance knowledge:"
    
    def _try_local_llm(self, prompt: str) -> Tuple[bool, str]:
        """Try local LLM using Ollama"""
        try:
            payload = {
                "model": self.local_model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "num_predict": 150
                }
            }
            
            response = requests.post(
                self.local_llm_url, 
                json=payload, 
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                answer = result.get("response", "").strip()
                return bool(answer), answer
            else:
                return False, f"Error {response.status_code}"
                
        except requests.exceptions.ConnectionError:
            return False, "Local LLM not available"
        except Exception as e:
            logger.error(f"Local LLM error: {str(e)}")
            return False, "Exception occurred"
    
    def _try_cloud_llm(self, prompt: str) -> str:
        """Try cloud LLM with fallback models"""
        for attempt in range(len(self.cloud_models)):
            model = self.cloud_models[self.current_model_index]
            
            try:
                response = self._call_cloud_api(prompt, model)
                if response:
                    return response
            except Exception as e:
                logger.warning(f"Model {model} failed: {str(e)}")
            
            # Try next model
            self.current_model_index = (self.current_model_index + 1) % len(self.cloud_models)
        
        return None
```

### 1.3 Data Layer Components

#### 1.3.1 SQLite Client (`database/sqlite_client.py`)
```python
class SQLiteClient:
    def __init__(self, db_path: str = "database.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Documents table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT UNIQUE NOT NULL,
                    file_name TEXT NOT NULL,
                    file_size INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    processed_at TIMESTAMP,
                    status TEXT DEFAULT 'pending'
                )
            """)
            
            # Clauses table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS clauses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    doc_id INTEGER NOT NULL,
                    vector_id TEXT UNIQUE NOT NULL,
                    clause_text TEXT NOT NULL,
                    clause_index INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (doc_id) REFERENCES documents (id)
                )
            """)
            
            # Query logs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS query_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    doc_id INTEGER,
                    query_text TEXT NOT NULL,
                    response_text TEXT NOT NULL,
                    processing_time REAL,
                    cache_hit BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (doc_id) REFERENCES documents (id)
                )
            """)
            
            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_documents_path ON documents(file_path)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_clauses_doc_id ON clauses(doc_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_clauses_vector_id ON clauses(vector_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_query_logs_doc_id ON query_logs(doc_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_query_logs_created_at ON query_logs(created_at)")
            
            conn.commit()
    
    def store_document(self, file_path: str, file_name: str, file_size: int = None) -> int:
        """Store document metadata and return document ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO documents (file_path, file_name, file_size, processed_at, status)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP, 'processed')
            """, (file_path, file_name, file_size))
            
            doc_id = cursor.lastrowid
            conn.commit()
            return doc_id
    
    def store_clauses(self, doc_id: int, clauses: List[str], vector_ids: List[str]):
        """Store document clauses with their vector IDs"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            for i, (clause, vector_id) in enumerate(zip(clauses, vector_ids)):
                cursor.execute("""
                    INSERT OR REPLACE INTO clauses (doc_id, vector_id, clause_text, clause_index)
                    VALUES (?, ?, ?, ?)
                """, (doc_id, vector_id, clause, i))
            
            conn.commit()
    
    def log_query(self, doc_id: int, query: str, response: str, processing_time: float, cache_hit: bool = False):
        """Log query and response for analytics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO query_logs (doc_id, query_text, response_text, processing_time, cache_hit)
                VALUES (?, ?, ?, ?, ?)
            """, (doc_id, query, response, processing_time, cache_hit))
            conn.commit()
    
    def get_document_id(self, file_path: str) -> Optional[int]:
        """Get document ID by file path"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM documents WHERE file_path = ?", (file_path,))
            result = cursor.fetchone()
            return result[0] if result else None
```

#### 1.3.2 Cache Manager (`core/cache_manager.py`)
```python
class CacheManager:
    def __init__(self, cache_file: str = "llm_cache.json"):
        self.cache_file = cache_file
        self.cache = self._load_cache()
        self.max_cache_size = 10000  # Maximum number of cached items
    
    def _load_cache(self) -> Dict[str, Dict]:
        """Load cache from file"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading cache: {str(e)}")
        return {}
    
    def _save_cache(self):
        """Save cache to file"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving cache: {str(e)}")
    
    def _get_cache_key(self, query: str, doc_id: int) -> str:
        """Generate cache key for query and document"""
        key_data = f"{query}_{doc_id}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get_cached_response(self, query: str, doc_id: int) -> Optional[str]:
        """Get cached response if available"""
        cache_key = self._get_cache_key(query, doc_id)
        cache_entry = self.cache.get(cache_key)
        
        if cache_entry:
            # Check if cache entry is still valid (24 hours)
            created_at = datetime.fromisoformat(cache_entry["created_at"])
            if datetime.now() - created_at < timedelta(hours=24):
                return cache_entry["response"]
            else:
                # Remove expired entry
                del self.cache[cache_key]
        
        return None
    
    def cache_response(self, query: str, doc_id: int, response: str):
        """Cache response for future use"""
        cache_key = self._get_cache_key(query, doc_id)
        
        # Check cache size and remove oldest entries if needed
        if len(self.cache) >= self.max_cache_size:
            self._cleanup_old_entries()
        
        self.cache[cache_key] = {
            "response": response,
            "created_at": datetime.now().isoformat(),
            "query": query,
            "doc_id": doc_id
        }
        
        self._save_cache()
    
    def _cleanup_old_entries(self):
        """Remove oldest cache entries to maintain size limit"""
        # Sort by creation time and remove oldest 20%
        entries = list(self.cache.items())
        entries.sort(key=lambda x: x[1]["created_at"])
        
        remove_count = len(entries) // 5  # Remove 20%
        for i in range(remove_count):
            del self.cache[entries[i][0]]
```

### 1.4 Configuration Management

#### 1.4.1 Settings Configuration (`config/settings.py`)
```python
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_RELOAD: bool = True
    
    # LLM Configuration
    OPENROUTER_API_KEY: str
    OPENROUTER_REFERER: str = "https://github.com/your-repo"
    USE_LOCAL_LLM: bool = True
    LOCAL_LLM_URL: str = "http://localhost:11434/api/generate"
    LOCAL_LLM_MODEL: str = "llama3.2:3b"
    
    # Database Configuration
    DATABASE_URL: str = "sqlite:///database.db"
    
    # File Processing Configuration
    TEMP_DIR: str = "temp"
    MAX_FILE_SIZE_MB: int = 100
    DOWNLOAD_TIMEOUT: int = 30
    TEMP_FILE_CLEANUP_RETRIES: int = 3
    TEMP_FILE_CLEANUP_DELAY: int = 5
    
    # Embedding Configuration
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384
    SIMILARITY_THRESHOLD: float = 0.05
    MAX_CLAUSE_SIZE: int = 40000
    
    # Caching Configuration
    CACHE_FILE: str = "llm_cache.json"
    MAX_CACHE_SIZE: int = 10000
    CACHE_TTL_HOURS: int = 24
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()
```

## 2. Database Schema

### 2.1 ERD (Entity Relationship Diagram)
```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   documents     │     │     clauses     │     │   query_logs    │
├─────────────────┤     ├─────────────────┤     ├─────────────────┤
│ id (PK)         │◄────┤ doc_id (FK)     │     │ id (PK)         │
│ file_path       │     │ vector_id (UK)  │     │ doc_id (FK)     │
│ file_name       │     │ clause_text     │     │ query_text      │
│ file_size       │     │ clause_index    │     │ response_text   │
│ created_at      │     │ created_at      │     │ processing_time │
│ processed_at    │     └─────────────────┘     │ cache_hit       │
│ status          │                              │ created_at      │
└─────────────────┘                              └─────────────────┘
```

### 2.2 Index Strategy
```sql
-- Primary indexes
CREATE INDEX idx_documents_path ON documents(file_path);
CREATE INDEX idx_documents_status ON documents(status);
CREATE INDEX idx_clauses_doc_id ON clauses(doc_id);
CREATE INDEX idx_clauses_vector_id ON clauses(vector_id);
CREATE INDEX idx_query_logs_doc_id ON query_logs(doc_id);
CREATE INDEX idx_query_logs_created_at ON query_logs(created_at);

-- Composite indexes for common queries
CREATE INDEX idx_clauses_doc_id_index ON clauses(doc_id, clause_index);
CREATE INDEX idx_query_logs_doc_time ON query_logs(doc_id, created_at);
```

## 3. API Endpoints Specification

### 3.1 Main Query Endpoint
```yaml
POST /api/v1/hackrx/run
Description: Process queries against insurance documents
Request Body:
  documents: string (required) - Document URL or path
  questions: array[string] (required) - List of questions to process

Response:
  200 OK:
    answers: array[string] - Generated answers
    doc_id: integer - Document ID
    processing_time: float - Total processing time
    cache_hit: boolean - Whether response was cached

  400 Bad Request:
    detail: string - Error description

  500 Internal Server Error:
    detail: string - Error description
```

### 3.2 Document Management Endpoints
```yaml
GET /api/v1/documents
Description: List all processed documents
Response:
  200 OK:
    documents: array[object] - List of document metadata

POST /api/v1/documents/upload
Description: Upload and process a new document
Request Body:
  file: file (required) - Document file
Response:
  200 OK:
    doc_id: integer - Document ID
    status: string - Processing status
```

### 3.3 Analytics Endpoints
```yaml
GET /api/v1/analytics/queries
Description: Get query analytics
Query Parameters:
  doc_id: integer (optional) - Filter by document ID
  start_date: string (optional) - Start date filter
  end_date: string (optional) - End date filter
Response:
  200 OK:
    total_queries: integer
    avg_processing_time: float
    cache_hit_rate: float
    top_queries: array[object]
```

## 4. Error Handling Strategy

### 4.1 Error Types and Codes
```python
class SystemError(Exception):
    """Base system error"""
    pass

class DocumentProcessingError(SystemError):
    """Document processing related errors"""
    pass

class LLMError(SystemError):
    """LLM processing related errors"""
    pass

class DatabaseError(SystemError):
    """Database related errors"""
    pass

class ValidationError(SystemError):
    """Input validation errors"""
    pass
```

### 4.2 Error Response Format
```python
class ErrorResponse(BaseModel):
    error_code: str
    message: str
    details: Optional[Dict] = None
    timestamp: datetime = Field(default_factory=datetime.now)

# Example error responses
ERROR_RESPONSES = {
    "DOCUMENT_NOT_FOUND": {
        "error_code": "DOC_001",
        "message": "Document not found or not processed"
    },
    "INVALID_FILE_FORMAT": {
        "error_code": "DOC_002", 
        "message": "Unsupported file format"
    },
    "LLM_SERVICE_UNAVAILABLE": {
        "error_code": "LLM_001",
        "message": "LLM service temporarily unavailable"
    },
    "RATE_LIMIT_EXCEEDED": {
        "error_code": "API_001",
        "message": "Rate limit exceeded"
    }
}
```

## 5. Performance Optimization

### 5.1 Caching Strategy
```python
# Multi-level caching approach
class CacheStrategy:
    def __init__(self):
        self.memory_cache = {}  # In-memory cache for hot data
        self.disk_cache = DiskCache()  # Persistent cache
        self.cache_ttl = 3600  # 1 hour TTL
    
    def get(self, key: str) -> Optional[str]:
        # Check memory cache first
        if key in self.memory_cache:
            return self.memory_cache[key]
        
        # Check disk cache
        value = self.disk_cache.get(key)
        if value:
            # Promote to memory cache
            self.memory_cache[key] = value
            return value
        
        return None
```

### 5.2 Database Optimization
```python
# Connection pooling
class DatabasePool:
    def __init__(self, max_connections: int = 10):
        self.pool = Queue(maxsize=max_connections)
        self._init_pool(max_connections)
    
    def get_connection(self) -> sqlite3.Connection:
        return self.pool.get()
    
    def return_connection(self, conn: sqlite3.Connection):
        self.pool.put(conn)
    
    def _init_pool(self, size: int):
        for _ in range(size):
            conn = sqlite3.connect(settings.DATABASE_URL)
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA cache_size=10000")
            self.pool.put(conn)
```

### 5.3 Vector Search Optimization
```python
# FAISS index optimization
class OptimizedFAISSIndex:
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)
        self.index = faiss.IndexIVFFlat(
            faiss.IndexFlatL2(dimension), 
            dimension, 
            min(4096, max(1, self.index.ntotal // 30))
        )
    
    def add_vectors(self, vectors: np.ndarray):
        """Add vectors in batches for better performance"""
        batch_size = 1000
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            self.index.add(batch)
    
    def search(self, query_vector: np.ndarray, k: int = 30):
        """Optimized search with proper training"""
        if not self.index.is_trained:
            # Train the index if needed
            self.index.train(self.get_all_vectors())
        
        return self.index.search(query_vector, k)
```

## 6. Testing Strategy

### 6.1 Unit Tests
```python
# Example unit test for Decision Engine
class TestDecisionEngine:
    def setup_method(self):
        self.engine = DecisionEngine()
        self.mock_llm_client = Mock()
        self.engine.llm_client = self.mock_llm_client
    
    def test_process_single_query_with_context(self):
        # Arrange
        query = "What is the coverage limit?"
        doc_id = 1
        expected_response = "The coverage limit is $50,000"
        
        self.mock_llm_client.generate_response.return_value = expected_response
        
        # Act
        result = self.engine.process_single_query(query, doc_id)
        
        # Assert
        assert result == expected_response
        self.mock_llm_client.generate_response.assert_called_once()
```

### 6.2 Integration Tests
```python
# Example integration test
class TestQueryProcessingIntegration:
    def test_end_to_end_query_processing(self):
        # Arrange
        client = TestClient(app)
        test_document = "test_policy.pdf"
        test_questions = ["What is the coverage limit?"]
        
        # Act
        response = client.post("/api/v1/hackrx/run", json={
            "documents": test_document,
            "questions": test_questions
        })
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "answers" in data
        assert len(data["answers"]) == 1
        assert data["answers"][0] is not None
```

### 6.3 Performance Tests
```python
# Example performance test
class TestPerformance:
    def test_query_response_time(self):
        # Arrange
        engine = DecisionEngine()
        query = "What are the policy exclusions?"
        doc_id = 1
        
        # Act
        start_time = time.time()
        result = engine.process_single_query(query, doc_id)
        end_time = time.time()
        
        # Assert
        processing_time = end_time - start_time
        assert processing_time < 2.0  # Should complete within 2 seconds
        assert result is not None
```

## 7. Deployment Configuration

### 7.1 Docker Configuration
```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p temp logs

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 7.2 Docker Compose
```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
      - USE_LOCAL_LLM=false
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    depends_on:
      - ollama
    restart: unless-stopped

  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    restart: unless-stopped

volumes:
  ollama_data:
```

---

*This Low-Level Design document provides detailed implementation specifications for the LLM Query Retrieval System, including component designs, database schemas, API specifications, and deployment configurations.* 