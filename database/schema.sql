CREATE TABLE documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    doc_url TEXT NOT NULL,
    doc_name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE clauses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    doc_id INTEGER,
    clause_text TEXT NOT NULL,
    vector_id TEXT NOT NULL,
    FOREIGN KEY (doc_id) REFERENCES documents(id)
);