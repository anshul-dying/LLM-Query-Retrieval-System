import os
import json
from datetime import datetime
from loguru import logger

class LoggerManager:
    def __init__(self):
        self.links_file = "links.log"
        self.queries_file = "queries.log"
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
    
    def log_document_link(self, document_url: str, doc_id: int, filename: str = None):
        """Log document link information"""
        try:
            timestamp = datetime.now().isoformat()
            log_entry = f"{timestamp}|{document_url}|{doc_id}|{filename or 'unknown'}\n"
            
            with open(self.links_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
            
            logger.info(f"Document link logged: {document_url} (ID: {doc_id})")
        except Exception as e:
            logger.error(f"Error logging document link: {str(e)}")
    
    def log_query(self, document_url: str, doc_id: int, query: str, response: str):
        """Log query and response information"""
        try:
            timestamp = datetime.now().isoformat()
            # Clean response for logging (remove newlines and limit length)
            clean_response = response.replace('\n', ' ').replace('\r', ' ')[:500]
            log_entry = f"{timestamp}|{document_url}|{doc_id}|{query}|{clean_response}\n"
            
            with open(self.queries_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
            
            logger.info(f"Query logged: {query[:50]}...")
        except Exception as e:
            logger.error(f"Error logging query: {str(e)}")
    
    def get_document_links(self) -> list[dict]:
        """Get all logged document links"""
        links = []
        try:
            if os.path.exists(self.links_file):
                with open(self.links_file, 'r', encoding='utf-8') as f:
                    for line in f:
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
        except Exception as e:
            logger.error(f"Error reading document links: {str(e)}")
        return links
    
    def get_queries_for_document(self, doc_id: int) -> list[dict]:
        """Get all queries for a specific document"""
        queries = []
        try:
            if os.path.exists(self.queries_file):
                with open(self.queries_file, 'r', encoding='utf-8') as f:
                    for line in f:
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
        except Exception as e:
            logger.error(f"Error reading queries: {str(e)}")
        return queries
    
    def get_all_queries(self) -> list[dict]:
        """Get all logged queries"""
        queries = []
        try:
            if os.path.exists(self.queries_file):
                with open(self.queries_file, 'r', encoding='utf-8') as f:
                    for line in f:
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
        except Exception as e:
            logger.error(f"Error reading all queries: {str(e)}")
        return queries 