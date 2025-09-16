import faiss
import os
from loguru import logger

index_path = "faiss_index.bin"
if not os.path.exists(index_path):
    logger.error("FAISS index not found. Run setup_faiss.py first.")
    exit(1)

index = faiss.read_index(index_path)
logger.info(f"FAISS index stats: {{'total_vectors': {index.ntotal}}}")