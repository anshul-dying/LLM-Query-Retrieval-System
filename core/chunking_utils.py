"""
Chunking utilities using LangChain's RecursiveCharacterTextSplitter
"""

from langchain_text_splitters import RecursiveCharacterTextSplitter
from loguru import logger


def chunk_clauses_optimized(clauses: list[str], pages: list[int | None] | None, max_clause_size: int = 40000) -> tuple[list[str], list[int | None]]:
    """
    Chunk multiple clauses using LangChain's RecursiveCharacterTextSplitter.
    Preserves page information for each chunk.
    
    Args:
        clauses: List of clause texts to chunk
        pages: List of page numbers corresponding to clauses (or None)
        max_clause_size: Maximum size in characters per chunk (default: 40000)
        
    Returns:
        Tuple of (chunked_clauses, chunked_pages)
    """
    if not clauses:
        return [], []
    
    # Initialize the recursive text splitter
    # chunk_size is in characters, chunk_overlap helps maintain context
    # Convert max_clause_size from bytes to characters (approximate, using 1:1 ratio)
    chunk_size = max_clause_size
    chunk_overlap = max(200, int(chunk_size * 0.1))  # 10% overlap or minimum 200 chars
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        # length_function=len,
        # separators=[
        #     "\n\n",      # Paragraph breaks
        #     "\n",        # Line breaks
        #     ". ",        # Sentence endings
        #     " ",         # Word boundaries
        #     "",          # Character boundaries (fallback)
        # ],
        # keep_separator=True,  # Keep separators in chunks for better context
    )
    
    chunked_clauses = []
    chunked_pages = []
    
    for idx, clause_text in enumerate(clauses):
        clause_page = pages[idx] if pages and idx < len(pages) else None
        
        if not clause_text or not clause_text.strip():
            # Skip empty clauses
            continue
        
        # Fast path: clause already fits within chunk size
        if len(clause_text) <= chunk_size:
            chunked_clauses.append(clause_text)
            chunked_pages.append(clause_page)
        else:
            # Use LangChain splitter to chunk this clause
            try:
                chunks = text_splitter.split_text(clause_text)
                
                # Assign the same page number to all chunks from this clause
                for chunk in chunks:
                    if chunk.strip():  # Only add non-empty chunks
                        chunked_clauses.append(chunk.strip())
                        chunked_pages.append(clause_page)
                
                logger.debug(f"Chunked clause {idx} into {len(chunks)} pieces (page: {clause_page})")
            except Exception as e:
                logger.error(f"Error chunking clause {idx}: {e}")
                # Fallback: add the original clause if chunking fails
                chunked_clauses.append(clause_text)
                chunked_pages.append(clause_page)
    
    logger.info(f"Chunked {len(clauses)} clauses into {len(chunked_clauses)} chunks")
    return chunked_clauses, chunked_pages


def chunk_text_optimized(text: str, max_size_bytes: int, page: int | None = None) -> tuple[list[str], list[int | None]]:
    """
    Chunk a single text using LangChain's RecursiveCharacterTextSplitter.
    Maintains backward compatibility with the old function signature.
    
    Args:
        text: Text to chunk
        max_size_bytes: Maximum size in bytes per chunk (converted to characters)
        page: Page number for the chunks
        
    Returns:
        Tuple of (chunked_texts, pages)
    """
    if not text or not text.strip():
        return [], []
    
    # Convert bytes to characters (approximate 1:1 for ASCII, but may vary for UTF-8)
    # For safety, use a slightly smaller chunk size
    chunk_size = int(max_size_bytes * 0.9)  # Use 90% to account for UTF-8 encoding
    chunk_overlap = max(200, int(chunk_size * 0.1))  # 10% overlap or minimum 200 chars
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=[
            "\n\n",      # Paragraph breaks
            "\n",        # Line breaks
            ". ",        # Sentence endings
            " ",         # Word boundaries
            "",          # Character boundaries (fallback)
        ],
        keep_separator=True,
    )
    
    try:
        chunks = text_splitter.split_text(text)
        # Filter out empty chunks and assign page numbers
        chunked_texts = [chunk.strip() for chunk in chunks if chunk.strip()]
        pages = [page] * len(chunked_texts)
        
        return chunked_texts, pages
    except Exception as e:
        logger.error(f"Error chunking text: {e}")
        # Fallback: return original text
        return [text], [page]
