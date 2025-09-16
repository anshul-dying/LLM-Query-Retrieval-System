# LLM Query Retrieval System

A sophisticated AI-powered system designed to intelligently process and answer queries from insurance policy documents. Built for the Bajaj Finserv Hackathon, this system combines advanced natural language processing with document analysis to provide accurate, context-aware responses to insurance-related questions.

## What is this project?

This is an intelligent document query system that:

- **Processes Insurance Documents**: Automatically extracts and analyzes text from PDF insurance policy documents
- **Semantic Search**: Uses advanced embedding technology to find the most relevant document sections for any query
- **Intelligent Answering**: Leverages Large Language Models (LLMs) to generate accurate, context-aware responses
- **RESTful API**: Provides a clean API interface for document processing and query handling
- **Analytics**: Tracks query patterns and provides insights into document usage
- **Intelligent Caching**: Implements sophisticated caching mechanisms for improved performance and cost optimization

The system is specifically designed for insurance policy documents but can be adapted for other document types. It handles complex queries by matching them against relevant document clauses and generating human-like responses.

## How to Setup this Project

### Prerequisites

- Python 3.10 or higher
- pip (Python package installer)
- Git

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/anshul-dying/Private-Private.git
   cd private-private
   ```

2. **Create a virtual environment**
   ```bash
   # Using Python
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate

   # Using Conda
   conda create -m venv python==3.10 or later
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   
   Create a `.env` file in the root directory with the following variables:
   ```env
   OPENROUTER_API_KEY=your_openrouter_api_key_here
   OPENROUTER_REFERER=https://github.com/your-repo
   USE_LOCAL_LLM=true
   LOCAL_LLM_URL=http://localhost:11434/api/generate
   LOCAL_LLM_MODEL=llama3.2:3b
   DATABASE_URL=sqlite:///database.db
   LOG_LEVEL=INFO
   ```

5. **Optional: Set up local LLM (Ollama)**
   If you prefer running a local LLM instead of using cloud-based services:

   ```bash
   # 1. Install Ollama (see: https://ollama.ai/)
   #    Follow the installation instructions for your OS.

   # 2. Pull the model you want
   ollama pull llama3.2:3b    # Example: LLaMA 3.2 with 3B parameters
                              # You can replace this with another model name.
                              # If you change the model, also update the `.env` file accordingly.

   # 3. Start the local Ollama server
   ollama serve
   ```

6. **Run the application**
   ```bash
   # Start the FastAPI server
   uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
   ```

7. **Access the API**
   
   The API will be available at `http://localhost:8000`
   - API Documentation: `http://localhost:8000/docs`
   - Alternative docs: `http://localhost:8000/redoc`

### Project Structure

```
├── api/                                  # FastAPI application
│   ├── main.py                           # Main application entry point
│   ├── routes/                           # API route definitions
│   └── models/                           # Pydantic models
├── core/                                 # Core business logic
│   ├── decision_engine.py                # Main decision making logic
│   ├── llm_client.py                     # LLM integration with caching
│   ├── embedding_generator.py            # Text embedding generation
│   ├── document_processor.py             # Document processing
│   ├── clause_matcher.py                 # Clause matching logic
│   └── logger_manager.py                 # Logging management
├── config/                               # Configuration files
├── database/                             # Database related files
├── Docs/                                 # Sample documents and queries
├── scripts/                              # Utility scripts
├── tests/                                # Test files
└── requirements.txt                      # Python dependencies
```

## How it Works

The system operates through several sophisticated components working together:

### 1. Document Processing
- **Text Extraction**: Documents are processed to extract text content using PyPDF2 and python-docx
- **Chunking**: Large documents are broken down into manageable clauses for better processing
- **Embedding Generation**: Each clause is converted into high-dimensional vector embeddings using sentence-transformers
- **Storage**: Document metadata and embeddings are stored in a SQLite database with FAISS indexing for fast retrieval

### 2. Query Processing
When a query is received, the system follows this workflow:

1. **Semantic Search**: Uses FAISS vector similarity search to find the most relevant document clauses
2. **Context Assembly**: Combines the most relevant clauses to provide context for the LLM
3. **Response Generation**: Sends the query and context to the LLM for answer generation

### 3. Intelligent Answering
The system employs multiple strategies for generating responses:

- **Context-Aware Generation**: For complex queries, provides relevant document context to the LLM
- **Fallback Responses**: When no relevant context is found, generates general insurance knowledge responses
- **Caching**: Implements intelligent caching to improve response times and reduce API costs

### 4. Caching System

The system implements a sophisticated multi-level caching strategy:

#### **LLM Response Caching**
- **Cache Location**: `llm_cache.json`
- **Cache Key**: MD5 hash of the prompt
- **Benefits**: 
  - Eliminates redundant API calls
  - Reduces response time from 2-5 seconds to milliseconds
  - Significantly reduces API costs
  - Improves system reliability

#### **Embedding Caching**
- **Cache Location**: `faiss_index.bin` and `clause_metadata.json`
- **Benefits**:
  - Prevents re-computation of document embeddings
  - Enables fast semantic search across large document collections
  - Maintains search performance as document count grows

#### **Cache Management**
- **Automatic Loading**: Cache is loaded on system startup
- **Persistent Storage**: Cache survives system restarts
- **Error Handling**: Graceful fallback when cache operations fail
- **Memory Efficient**: Uses file-based storage for large datasets

#### **Cache Performance Impact**
```
Without Caching:
- First query: 3-5 seconds
- Repeated queries: 3-5 seconds each
- API calls: 1 per query

With Caching:
- First query: 3-5 seconds
- Repeated queries: 50-100 milliseconds
- API calls: 0 for cached queries
```

### 5. API Endpoints

The system provides several RESTful endpoints:

- `POST /api/v1/hackrx/run`: Main endpoint for processing queries against documents
- `GET /api/v1/documents`: Retrieve document information
- `GET /api/v1/analytics`: Access query analytics and insights

### 6. Performance Features

- **Batch Processing**: Handles multiple queries efficiently
- **Rate Limiting**: Manages API calls to prevent overloading
- **Model Fallback**: Automatically switches between different LLM models if one fails
- **Local/Cloud LLM Support**: Can use either local Ollama models or cloud-based APIs
- **Intelligent Caching**: Multi-level caching for optimal performance

### Example Usage

```bash
# Process queries against a document
curl -X POST "http://localhost:8000/api/v1/hackrx/run" \
  -H "Content-Type: application/json" \
  -d '{
    "documents": "path/to/insurance_policy.pdf",
    "questions": [
      "What is the coverage limit for medical expenses?",
      "What are the exclusions in this policy?"
    ]
  }'
```

The system will return structured responses with accurate answers based on the document content and intelligent analysis. Subsequent queries with similar content will be served from cache for near-instantaneous responses.
