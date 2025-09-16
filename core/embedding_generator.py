import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from loguru import logger
import os
import json

class EmbeddingGenerator:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.index_path = "faiss_index.bin"
        self.metadata_path = "clause_metadata.json"
        self.dimension = 384
        self.index = faiss.read_index(self.index_path) if os.path.exists(self.index_path) else faiss.IndexFlatL2(self.dimension)
        self.clause_metadata = self._load_metadata()
        self.vector_count = self.index.ntotal

    def _load_metadata(self):
        """Load clause metadata from JSON file"""
        if os.path.exists(self.metadata_path):
            try:
                with open(self.metadata_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading metadata: {str(e)}")
                return {}
        return {}

    def _save_metadata(self):
        """Save clause metadata to JSON file"""
        try:
            with open(self.metadata_path, 'w', encoding='utf-8') as f:
                json.dump(self.clause_metadata, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving metadata: {str(e)}")

    def generate_embeddings(self, clauses: list[str], doc_id: int) -> list[str]:
        try:
            embeddings = self.model.encode(clauses, show_progress_bar=False, batch_size=16)
            vector_ids = []
            
            # Load existing metadata to preserve other documents
            existing_metadata = self._load_metadata()
            
            for i, (clause, embedding) in enumerate(zip(clauses, embeddings)):
                vector_id = f"{doc_id}_{i}"
                self.index.add(np.array([embedding]).astype('float32'))
                existing_metadata[vector_id] = {"clause": clause, "doc_id": doc_id}
                vector_ids.append(vector_id)
            
            # Update the metadata with all documents
            self.clause_metadata = existing_metadata
            self.vector_count = self.index.ntotal
            faiss.write_index(self.index, self.index_path)
            self._save_metadata()
            logger.info(f"Stored {len(vector_ids)} embeddings for doc_id {doc_id}, total vectors: {self.vector_count}")
            return vector_ids
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            logger.error(f"Exception type: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def search_similar_clauses(self, query: str, top_k: int = 30, doc_id: int = None) -> list[dict]:
        try:
            query_embedding = self.model.encode([query])[0].astype('float32')
            distances, indices = self.index.search(np.array([query_embedding]), top_k)
            results = []
            metadata_keys = list(self.clause_metadata.keys())
            
            logger.info(f"Searching for query: {query[:50]}...")
            logger.info(f"Total vectors in index: {self.vector_count}")
            logger.info(f"Total metadata keys: {len(metadata_keys)}")
            if doc_id:
                logger.info(f"Filtering for doc_id: {doc_id}")
            
            for idx, distance in zip(indices[0], distances[0]):
                if idx != -1 and idx < len(metadata_keys):
                    vector_id = metadata_keys[idx]
                    clause_data = self.clause_metadata[vector_id]
                    
                    # Filter by document ID if specified
                    if doc_id is not None and clause_data["doc_id"] != doc_id:
                        continue
                    
                    score = 1 / (1 + distance)
                    # Lower threshold to be more lenient
                    if score > 0.05:  # Much lower threshold
                        results.append({"clause": clause_data["clause"], "score": float(score)})
                        logger.info(f"Found clause with score {score:.3f}: {clause_data['clause'][:100]}...")
            
            logger.info(f"Found {len(results)} similar clauses for query")
            return results
        except Exception as e:
            logger.error(f"Error searching similar clauses: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return []