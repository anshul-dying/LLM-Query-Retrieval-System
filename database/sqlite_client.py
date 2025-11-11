import sqlite3
from loguru import logger
import os
from contextlib import contextmanager
from threading import local

class SQLiteClient:
    def __init__(self):
        self.db_path = "database.db"
        self._thread_local = local()
        self.create_schema()

    @contextmanager
    def _get_connection(self):
        """Get a connection with optimizations, reusing connection in same thread if possible"""
        if not hasattr(self._thread_local, 'connection') or self._thread_local.connection is None:
            conn = sqlite3.connect(self.db_path)
            # Performance optimizations
            conn.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging for better concurrency
            conn.execute("PRAGMA synchronous=NORMAL")  # Balance between safety and speed
            conn.execute("PRAGMA cache_size=-64000")  # 64MB cache
            conn.execute("PRAGMA temp_store=MEMORY")  # Store temp tables in memory
            conn.execute("PRAGMA mmap_size=268435456")  # 256MB memory-mapped I/O
            self._thread_local.connection = conn
        else:
            conn = self._thread_local.connection
        
        try:
            yield conn
        except Exception:
            conn.rollback()
            raise

    def create_schema(self):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS documents (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        url TEXT UNIQUE,
                        filename TEXT
                    )
                """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS clauses (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        doc_id INTEGER,
                        clause_text TEXT,
                        vector_id TEXT,
                        page INTEGER,
                        FOREIGN KEY (doc_id) REFERENCES documents (id)
                    )
                """)
                # Backward-compatible migration: ensure 'page' column exists
                try:
                    cursor.execute("PRAGMA table_info(clauses)")
                    cols = [row[1] for row in cursor.fetchall()]
                    if 'page' not in cols:
                        cursor.execute("ALTER TABLE clauses ADD COLUMN page INTEGER")
                except Exception as _:
                    # Ignore migration errors; table creation above includes page for fresh DBs
                    pass
                
                # Create indexes for performance optimization
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_clauses_doc_id ON clauses(doc_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_clauses_vector_id ON clauses(vector_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_documents_url ON documents(url)")
                
                conn.commit()
                logger.info("SQLite schema created with indexes.")
        except Exception as e:
            logger.error(f"Error creating schema: {str(e)}")

    def store_document(self, url: str, filename: str) -> int:
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT OR REPLACE INTO documents (url, filename) VALUES (?, ?)",
                    (url, filename)
                )
                conn.commit()
                cursor.execute("SELECT id FROM documents WHERE url = ?", (url,))
                doc_id = cursor.fetchone()[0]
                logger.info(f"Stored document: {filename}, ID: {doc_id}")
                return doc_id
        except Exception as e:
            logger.error(f"Error storing document: {str(e)}")
            raise

    def get_document_id(self, url: str) -> int:
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM documents WHERE url = ?", (url,))
                result = cursor.fetchone()
                return result[0] if result else None
        except Exception as e:
            logger.error(f"Error retrieving document ID: {str(e)}")
            return None

    def store_clauses(self, doc_id: int, clauses: list[str], vector_ids: list[str], pages: list[int | None] | None = None):
        """Optimized batch insert using executemany for better performance"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                # Prepare batch data for executemany
                batch_data = []
                for idx, (clause, vector_id) in enumerate(zip(clauses, vector_ids)):
                    page_val = pages[idx] if pages is not None and idx < len(pages) else None
                    batch_data.append((doc_id, clause, vector_id, page_val))
                
                # Use executemany for batch insert - much faster than individual inserts
                cursor.executemany(
                    "INSERT INTO clauses (doc_id, clause_text, vector_id, page) VALUES (?, ?, ?, ?)",
                    batch_data
                )
                conn.commit()
                logger.info(f"Stored {len(clauses)} clauses for doc_id {doc_id} (batch insert)")
        except Exception as e:
            logger.error(f"Error storing clauses: {str(e)}")
            raise

    def get_all_clauses(self):
        """Get all clauses from the database"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT doc_id, clause_text, vector_id FROM clauses")
                results = cursor.fetchall()
                return [
                    {
                        'doc_id': row[0],
                        'clause_text': row[1],
                        'vector_id': row[2]
                    }
                    for row in results
                ]
        except Exception as e:
            logger.error(f"Error retrieving all clauses: {str(e)}")
            return []