import faiss
import os
from loguru import logger

def setup_faiss_index():
    index_path = "faiss_index.bin"
    dimension = 384  # Matches all-MiniLM-L6-v2
    if not os.path.exists(index_path):
        index = faiss.IndexFlatL2(dimension)
        faiss.write_index(index, index_path)
        logger.info(f"FAISS index created at {index_path}")
    else:
        logger.info(f"FAISS index already exists at {index_path}")

if __name__ == "__main__":
    setup_faiss_index()