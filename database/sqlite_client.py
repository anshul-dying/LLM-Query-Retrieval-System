import sqlite3
from loguru import logger
import os

class SQLiteClient:
    def __init__(self):
        self.db_path = "database.db"
        self.create_schema()

    def create_schema(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
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
                        FOREIGN KEY (doc_id) REFERENCES documents (id)
                    )
                """)
                conn.commit()
                logger.info("SQLite schema created.")
        except Exception as e:
            logger.error(f"Error creating schema: {str(e)}")

    def store_document(self, url: str, filename: str) -> int:
        try:
            with sqlite3.connect(self.db_path) as conn:
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
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM documents WHERE url = ?", (url,))
                result = cursor.fetchone()
                return result[0] if result else None
        except Exception as e:
            logger.error(f"Error retrieving document ID: {str(e)}")
            return None

    def store_clauses(self, doc_id: int, clauses: list[str], vector_ids: list[str]):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                for clause, vector_id in zip(clauses, vector_ids):
                    cursor.execute(
                        "INSERT INTO clauses (doc_id, clause_text, vector_id) VALUES (?, ?, ?)",
                        (doc_id, clause, vector_id)
                    )
                conn.commit()
                logger.info(f"Stored {len(clauses)} clauses for doc_id {doc_id}")
        except Exception as e:
            logger.error(f"Error storing clauses: {str(e)}")
            raise

    def get_all_clauses(self):
        """Get all clauses from the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
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