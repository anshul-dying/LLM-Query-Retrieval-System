"""
Optimized chunking utilities for text processing
"""

def chunk_text_optimized(text: str, max_size_bytes: int, page: int | None = None) -> tuple[list[str], list[int | None]]:
    """
    Optimized text chunking that avoids word-by-word iteration.
    Uses binary search and efficient byte calculations.
    
    Args:
        text: Text to chunk
        max_size_bytes: Maximum size in bytes per chunk
        page: Page number for the chunks
        
    Returns:
        Tuple of (chunked_texts, pages)
    """
    if not text:
        return [], []
    
    # Fast path: if text fits, return as-is
    encoded_text = text.encode('utf-8')
    if len(encoded_text) <= max_size_bytes:
        return [text], [page]
    
    chunks = []
    pages = []
    
    # Use more efficient chunking with binary search approach
    # Instead of word-by-word, chunk by character positions
    start = 0
    text_len = len(text)
    
    while start < text_len:
        # Estimate chunk end position
        end = start + int((max_size_bytes * text_len) / len(encoded_text))
        end = min(end, text_len)
        
        # Binary search for the best split point near a word boundary
        chunk_candidate = text[start:end]
        chunk_bytes = len(chunk_candidate.encode('utf-8'))
        
        if chunk_bytes <= max_size_bytes:
            # Try to extend to max size by finding next word boundary
            remaining = text_len - end
            extend_by = min(remaining, int((max_size_bytes - chunk_bytes) * text_len / len(encoded_text)))
            if extend_by > 0:
                # Find nearest word boundary for extension
                extend_end = end + extend_by
                extend_end = min(extend_end, text_len)
                # Look for space/sentence boundary near the end
                for search_pos in range(extend_end - 1, end - 1, -1):
                    if text[search_pos] in (' ', '.', '!', '?', '\n'):
                        extend_end = search_pos + 1
                        break
                
                candidate = text[start:extend_end]
                if len(candidate.encode('utf-8')) <= max_size_bytes:
                    chunk_candidate = candidate
                    end = extend_end
        
        # Ensure we don't exceed max size
        while len(chunk_candidate.encode('utf-8')) > max_size_bytes:
            # Find last space or sentence boundary
            last_space = chunk_candidate.rfind(' ', 0, len(chunk_candidate) - 1)
            last_period = chunk_candidate.rfind('.', 0, len(chunk_candidate) - 1)
            split_pos = max(last_space, last_period)
            
            if split_pos > 0:
                chunk_candidate = chunk_candidate[:split_pos + 1]
                end = start + split_pos + 1
            else:
                # Force split even if no boundary found
                # Find safe UTF-8 boundary
                bytes_so_far = chunk_candidate.encode('utf-8')
                if len(bytes_so_far) > max_size_bytes:
                    # Truncate at safe UTF-8 boundary
                    safe_bytes = bytes_so_far[:max_size_bytes]
                    while len(safe_bytes) > 0 and safe_bytes[-1] & 0xC0 == 0x80:
                        safe_bytes = safe_bytes[:-1]
                    chunk_candidate = safe_bytes.decode('utf-8', errors='ignore')
                    end = start + len(chunk_candidate)
                break
        
        chunks.append(chunk_candidate.strip())
        pages.append(page)
        start = end
    
    return chunks, pages


def chunk_clauses_optimized(clauses: list[str], pages: list[int | None] | None, max_clause_size: int = 40000) -> tuple[list[str], list[int | None]]:
    """
    Optimized batch chunking of multiple clauses.
    
    Args:
        clauses: List of clause texts
        pages: List of page numbers (or None)
        max_clause_size: Maximum size in bytes per clause
        
    Returns:
        Tuple of (chunked_clauses, chunked_pages)
    """
    if not clauses:
        return [], []
    
    chunked_clauses = []
    chunked_pages = []
    
    for idx, clause_text in enumerate(clauses):
        clause_page = pages[idx] if pages and idx < len(pages) else None
        
        # Fast path: clause already fits
        if len(clause_text.encode('utf-8')) <= max_clause_size:
            chunked_clauses.append(clause_text)
            chunked_pages.append(clause_page)
        else:
            # Chunk this clause
            chunks, chunk_pages = chunk_text_optimized(clause_text, max_clause_size, clause_page)
            chunked_clauses.extend(chunks)
            chunked_pages.extend(chunk_pages)
    
    return chunked_clauses, chunked_pages

