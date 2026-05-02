import faiss
import numpy as np
from typing import List, Tuple

class VectorStore:
    """
    Enhanced vector store for efficient similarity search.
    Uses FAISS for fast nearest neighbor search.
    """
    
    def __init__(self, dim):
        """
        Initialize vector store.
        
        Args:
            dim: Dimension of embedding vectors
        """
        # Use IndexFlatIP for inner product similarity (cosine similarity with normalized vectors)
        self.index = faiss.IndexFlatIP(dim)
        self.texts = []
        self.metadata = []  # Store additional metadata for each text
        self.dim = dim
    
    def add(self, embeddings, texts, metadata=None):
        """
        Add embeddings and corresponding texts to the store.
        
        Args:
            embeddings: Numpy array of embeddings
            texts: List of text strings
            metadata: Optional list of metadata dictionaries
        """
        if not isinstance(embeddings, np.ndarray):
            embeddings = np.array(embeddings)
        
        # Ensure embeddings are float32 (required by FAISS)
        embeddings = embeddings.astype('float32')
        
        # Add to index
        self.index.add(embeddings)
        
        # Store texts
        self.texts.extend(texts)
        
        # Store metadata
        if metadata:
            self.metadata.extend(metadata)
        else:
            self.metadata.extend([{}] * len(texts))
    
    def search(self, embedding, k=3):
        """
        Search for most similar texts.
        
        Args:
            embedding: Query embedding vector
            k: Number of results to return
        
        Returns:
            List of tuples (similarity_score, text)
        """
        if not isinstance(embedding, np.ndarray):
            embedding = np.array(embedding)
        
        # Ensure correct shape and type
        if embedding.ndim == 1:
            embedding = embedding.reshape(1, -1)
        embedding = embedding.astype('float32')
        
        # Ensure k doesn't exceed number of items in index
        k = min(k, self.index.ntotal)
        
        if k == 0:
            return []
        
        # Search
        scores, indices = self.index.search(embedding, k)
        
        # Build results
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx != -1:  # FAISS returns -1 for invalid indices
                results.append((float(score), self.texts[idx]))
        
        return results
    
    def search_with_metadata(self, embedding, k=3):
        """
        Search for most similar texts with metadata.
        
        Args:
            embedding: Query embedding vector
            k: Number of results to return
        
        Returns:
            List of tuples (similarity_score, text, metadata)
        """
        if not isinstance(embedding, np.ndarray):
            embedding = np.array(embedding)
        
        # Ensure correct shape and type
        if embedding.ndim == 1:
            embedding = embedding.reshape(1, -1)
        embedding = embedding.astype('float32')
        
        # Ensure k doesn't exceed number of items in index
        k = min(k, self.index.ntotal)
        
        if k == 0:
            return []
        
        # Search
        scores, indices = self.index.search(embedding, k)
        
        # Build results with metadata
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx != -1:
                metadata = self.metadata[idx] if idx < len(self.metadata) else {}
                results.append((float(score), self.texts[idx], metadata))
        
        return results
    
    def get_size(self):
        """Get number of vectors in the store."""
        return self.index.ntotal
    
    def clear(self):
        """Clear all stored vectors and texts."""
        self.index.reset()
        self.texts = []
        self.metadata = []
