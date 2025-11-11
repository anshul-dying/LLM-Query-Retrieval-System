import os
import json
from datetime import datetime
from loguru import logger
from threading import Lock
from collections import deque
import time

class LoggerManager:
    def __init__(self):
        self.links_file = "links.log"
        self.queries_file = "queries.log"
        self._write_buffer = deque(maxlen=100)  # Buffer for batch writes
        self._cache = {}  # Cache for read operations
        self._cache_timeout = 30  # Cache timeout in seconds
        self._last_cache_update = {}  # Track cache update times
        self._lock = Lock()  # Thread-safe operations
        self._last_flush = time.time()
        self._flush_interval = 5  # Flush buffer every 5 seconds
        self.ensure_log_files()
    
    def ensure_log_files(self):
        """Ensure log files exist with proper headers"""
        if not os.path.exists(self.links_file):
            with open(self.links_file, 'w', encoding='utf-8') as f:
                f.write("# Document Links Log\n")
                f.write("# Format: timestamp|document_url|doc_id|filename\n")
                f.write("# " + "="*50 + "\n")
        
        if not os.path.exists(self.queries_file):
            with open(self.queries_file, 'w', encoding='utf-8') as f:
                f.write("# Queries Log\n")
                f.write("# Format: timestamp|document_url|doc_id|query|response\n")
                f.write("# " + "="*50 + "\n")
    
    def _flush_buffer(self):
        """Flush write buffer to disk"""
        if not self._write_buffer:
            return
        
        with self._lock:
            if not self._write_buffer:
                return
            
            # Group writes by file for efficiency
            links_entries = []
            queries_entries = []
            
            for entry_type, entry in list(self._write_buffer):
                if entry_type == 'link':
                    links_entries.append(entry)
                elif entry_type == 'query':
                    queries_entries.append(entry)
            
            # Batch write links
            if links_entries:
                try:
                    with open(self.links_file, 'a', encoding='utf-8') as f:
                        f.writelines(links_entries)
                    # Invalidate cache
                    if 'links' in self._cache:
                        del self._cache['links']
                except Exception as e:
                    logger.error(f"Error flushing links buffer: {str(e)}")
            
            # Batch write queries
            if queries_entries:
                try:
                    with open(self.queries_file, 'a', encoding='utf-8') as f:
                        f.writelines(queries_entries)
                    # Invalidate cache
                    if 'queries' in self._cache:
                        del self._cache['queries']
                except Exception as e:
                    logger.error(f"Error flushing queries buffer: {str(e)}")
            
            self._write_buffer.clear()
            self._last_flush = time.time()
    
    def log_document_link(self, document_url: str, doc_id: int, filename: str = None):
        """Log document link information with buffered writes"""
        try:
            timestamp = datetime.now().isoformat()
            log_entry = f"{timestamp}|{document_url}|{doc_id}|{filename or 'unknown'}\n"
            
            # Add to buffer instead of immediate write
            with self._lock:
                self._write_buffer.append(('link', log_entry))
            
            # Flush if buffer is full or time elapsed
            current_time = time.time()
            if len(self._write_buffer) >= 100 or (current_time - self._last_flush) >= self._flush_interval:
                self._flush_buffer()
            
            logger.info(f"Document link logged: {document_url} (ID: {doc_id})")
        except Exception as e:
            logger.error(f"Error logging document link: {str(e)}")
    
    def log_query(self, document_url: str, doc_id: int, query: str, response: str | dict):
        """Log query and response information with buffered writes"""
        try:
            timestamp = datetime.now().isoformat()
            
            # Handle both string and dict responses
            if isinstance(response, dict):
                # Extract answer from dict if present, otherwise convert whole dict to string
                response_text = response.get("answer", str(response))
            else:
                response_text = str(response)
            
            # Clean response for logging (remove newlines and limit length)
            clean_response = response_text.replace('\n', ' ').replace('\r', ' ')[:500]
            log_entry = f"{timestamp}|{document_url}|{doc_id}|{query}|{clean_response}\n"
            
            # Add to buffer instead of immediate write
            with self._lock:
                self._write_buffer.append(('query', log_entry))
            
            # Flush if buffer is full or time elapsed
            current_time = time.time()
            if len(self._write_buffer) >= 100 or (current_time - self._last_flush) >= self._flush_interval:
                self._flush_buffer()
            
            logger.info(f"Query logged: {query[:50]}...")
        except Exception as e:
            logger.error(f"Error logging query: {str(e)}")
    
    def get_document_links(self) -> list[dict]:
        """Get all logged document links with caching"""
        # Flush buffer first to ensure we have latest data
        self._flush_buffer()
        
        # Check cache
        cache_key = 'links'
        current_time = time.time()
        if cache_key in self._cache:
            last_update = self._last_cache_update.get(cache_key, 0)
            if current_time - last_update < self._cache_timeout:
                return self._cache[cache_key]
        
        links = []
        try:
            if os.path.exists(self.links_file):
                # Use readlines for better performance than line-by-line iteration
                with open(self.links_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    for line in lines:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            parts = line.split('|')
                            if len(parts) >= 4:
                                links.append({
                                    'timestamp': parts[0],
                                    'document_url': parts[1],
                                    'doc_id': int(parts[2]),
                                    'filename': parts[3]
                                })
                # Cache the result
                with self._lock:
                    self._cache[cache_key] = links
                    self._last_cache_update[cache_key] = current_time
        except Exception as e:
            logger.error(f"Error reading document links: {str(e)}")
        return links
    
    def get_queries_for_document(self, doc_id: int) -> list[dict]:
        """Get all queries for a specific document with caching"""
        # Flush buffer first
        self._flush_buffer()
        
        # Check cache with doc_id key
        cache_key = f'queries_doc_{doc_id}'
        current_time = time.time()
        if cache_key in self._cache:
            last_update = self._last_cache_update.get(cache_key, 0)
            if current_time - last_update < self._cache_timeout:
                return self._cache[cache_key]
        
        queries = []
        try:
            if os.path.exists(self.queries_file):
                # Use readlines for better performance
                with open(self.queries_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    for line in lines:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            parts = line.split('|')
                            if len(parts) >= 5 and int(parts[2]) == doc_id:
                                queries.append({
                                    'timestamp': parts[0],
                                    'document_url': parts[1],
                                    'doc_id': int(parts[2]),
                                    'query': parts[3],
                                    'response': parts[4]
                                })
                # Cache the result
                with self._lock:
                    self._cache[cache_key] = queries
                    self._last_cache_update[cache_key] = current_time
        except Exception as e:
            logger.error(f"Error reading queries: {str(e)}")
        return queries
    
    def get_all_queries(self) -> list[dict]:
        """Get all logged queries with caching"""
        # Flush buffer first
        self._flush_buffer()
        
        # Check cache
        cache_key = 'queries'
        current_time = time.time()
        if cache_key in self._cache:
            last_update = self._last_cache_update.get(cache_key, 0)
            if current_time - last_update < self._cache_timeout:
                return self._cache[cache_key]
        
        queries = []
        try:
            if os.path.exists(self.queries_file):
                # Use readlines for better performance
                with open(self.queries_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    for line in lines:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            parts = line.split('|')
                            if len(parts) >= 5:
                                queries.append({
                                    'timestamp': parts[0],
                                    'document_url': parts[1],
                                    'doc_id': int(parts[2]),
                                    'query': parts[3],
                                    'response': parts[4]
                                })
                # Cache the result
                with self._lock:
                    self._cache[cache_key] = queries
                    self._last_cache_update[cache_key] = current_time
        except Exception as e:
            logger.error(f"Error reading all queries: {str(e)}")
        return queries 