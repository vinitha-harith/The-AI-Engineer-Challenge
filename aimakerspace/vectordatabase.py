"""
Vector Database with Metadata Support (Production Version)

This module provides efficient vector storage and similarity search using numpy.
For Vercel deployment, use the self-contained index_vercel.py instead.
"""

import json
import os
import urllib.request
from collections import defaultdict
from typing import List, Tuple, Callable, Dict, Any, Optional
from aimakerspace.openai_utils.embedding import EmbeddingModel
import asyncio
import numpy as np


# ============ Similarity Measures (numpy optimized) ============

def cosine_similarity(vector_a: np.ndarray, vector_b: np.ndarray) -> float:
    """
    Computes the cosine similarity between two vectors.
    
    Cosine similarity = (A · B) / (||A|| * ||B||)
    Range: [-1, 1] where 1 = identical direction
    """
    dot_product = np.dot(vector_a, vector_b)
    norm_a = np.linalg.norm(vector_a)
    norm_b = np.linalg.norm(vector_b)
    
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(dot_product / (norm_a * norm_b))


def euclidean_distance(vector_a: np.ndarray, vector_b: np.ndarray) -> float:
    """
    Computes the euclidean distance between two vectors.
    Returns negative distance so higher values = more similar (for consistent sorting).
    
    Euclidean distance = ||A - B||
    """
    distance = np.linalg.norm(vector_a - vector_b)
    return -float(distance)  # Negative so higher = more similar


def dot_product_similarity(vector_a: np.ndarray, vector_b: np.ndarray) -> float:
    """
    Computes the dot product between two vectors.
    
    Useful for normalized vectors or when magnitude matters.
    """
    return float(np.dot(vector_a, vector_b))


def manhattan_distance(vector_a: np.ndarray, vector_b: np.ndarray) -> float:
    """
    Computes the Manhattan (L1) distance between two vectors.
    Returns negative distance so higher values = more similar.
    
    Manhattan distance = Σ|Ai - Bi|
    """
    distance = np.sum(np.abs(vector_a - vector_b))
    return -float(distance)


def jaccard_similarity(vector_a: np.ndarray, vector_b: np.ndarray) -> float:
    """
    Computes Jaccard-like similarity for continuous vectors.
    Uses the ratio of minimum to maximum values element-wise.
    
    Jaccard = Σmin(|Ai|, |Bi|) / Σmax(|Ai|, |Bi|)
    Range: [0, 1] where 1 = identical
    """
    min_sum = np.sum(np.minimum(np.abs(vector_a), np.abs(vector_b)))
    max_sum = np.sum(np.maximum(np.abs(vector_a), np.abs(vector_b)))
    
    if max_sum == 0:
        return 0.0
    return float(min_sum / max_sum)


# Map of similarity measure names to functions
SIMILARITY_MEASURES = {
    "cosine": cosine_similarity,
    "euclidean": euclidean_distance,
    "dot_product": dot_product_similarity,
    "manhattan": manhattan_distance,
    "jaccard": jaccard_similarity,
}


def _to_numpy(data) -> np.ndarray:
    """Convert list or array to numpy array."""
    if isinstance(data, np.ndarray):
        return data
    return np.array(data, dtype=np.float32)


def _to_list(data) -> List[float]:
    """Convert numpy array to list for JSON serialization."""
    if isinstance(data, np.ndarray):
        return data.tolist()
    return list(data)


class VectorDatabase:
    """
    Basic vector database for similarity search.
    
    Stores vectors as numpy arrays for efficient computation.
    """
    
    def __init__(self, embedding_model: EmbeddingModel = None):
        self.vectors: Dict[str, np.ndarray] = defaultdict(lambda: np.array([]))
        self.embedding_model = embedding_model or EmbeddingModel()

    def insert(self, key: str, vector: np.ndarray) -> None:
        """Insert a vector with the given key."""
        self.vectors[key] = _to_numpy(vector)

    def search(
        self,
        query_vector: np.ndarray,
        k: int,
        distance_measure: Callable = cosine_similarity,
    ) -> List[Tuple[str, float]]:
        """
        Search for the k most similar vectors.
        
        Args:
            query_vector: The query embedding
            k: Number of results to return
            distance_measure: Similarity function to use
            
        Returns:
            List of (text, score) tuples sorted by similarity
        """
        query_np = _to_numpy(query_vector)
        scores = [
            (key, distance_measure(query_np, vector))
            for key, vector in self.vectors.items()
        ]
        return sorted(scores, key=lambda x: x[1], reverse=True)[:k]

    def search_by_text(
        self,
        query_text: str,
        k: int,
        distance_measure: Callable = cosine_similarity,
        return_as_text: bool = False,
    ) -> List[Tuple[str, float]]:
        """Search by text query."""
        query_vector = self.embedding_model.get_embedding(query_text)
        results = self.search(query_vector, k, distance_measure)
        return [result[0] for result in results] if return_as_text else results

    def retrieve_from_key(self, key: str) -> Optional[np.ndarray]:
        """Retrieve vector by key."""
        return self.vectors.get(key)

    async def abuild_from_list(self, list_of_text: List[str]) -> "VectorDatabase":
        """Build database from list of texts asynchronously."""
        embeddings = await self.embedding_model.async_get_embeddings(list_of_text)
        for text, embedding in zip(list_of_text, embeddings):
            self.insert(text, embedding)
        return self


class MetadataVectorDatabase:
    """
    Enhanced Vector Database with metadata support for filtering.
    
    Production version with numpy optimization.
    
    Supports:
    - Topic categories (exercise, nutrition, sleep, stress, habits, health)
    - Difficulty levels (beginner, intermediate, advanced)
    - Source file tracking
    - Multiple similarity measures
    - Save/load to JSON files or URLs
    """
    
    def __init__(self, embedding_model: EmbeddingModel = None):
        self.vectors: Dict[str, np.ndarray] = {}
        self.metadata: Dict[str, Dict[str, Any]] = {}
        self.embedding_model = embedding_model or EmbeddingModel()
        self.default_similarity = cosine_similarity

    def insert(
        self, 
        key: str, 
        vector: np.ndarray, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Insert a vector with optional metadata."""
        self.vectors[key] = _to_numpy(vector)
        self.metadata[key] = metadata or {}

    def search(
        self,
        query_vector: np.ndarray,
        k: int,
        distance_measure: Callable = None,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[Tuple[str, float, Dict[str, Any]]]:
        """
        Search for similar vectors with optional metadata filtering.
        
        Args:
            query_vector: The query embedding
            k: Number of results to return
            distance_measure: Similarity function to use
            filter_metadata: Dict of metadata key-value pairs to filter by
            
        Returns:
            List of (text, score, metadata) tuples
        """
        distance_measure = distance_measure or self.default_similarity
        query_np = _to_numpy(query_vector)
        
        # Filter vectors by metadata if specified
        filtered_keys = list(self.vectors.keys())
        if filter_metadata:
            filtered_keys = [
                key for key in filtered_keys
                if self._matches_filter(self.metadata.get(key, {}), filter_metadata)
            ]
        
        # Calculate scores using numpy
        scores = [
            (key, distance_measure(query_np, self.vectors[key]), self.metadata.get(key, {}))
            for key in filtered_keys
        ]
        
        return sorted(scores, key=lambda x: x[1], reverse=True)[:k]

    def _matches_filter(self, metadata: Dict[str, Any], filter_metadata: Dict[str, Any]) -> bool:
        """Check if metadata matches the filter criteria."""
        for key, value in filter_metadata.items():
            if key not in metadata:
                return False
            if isinstance(value, list):
                if metadata[key] not in value:
                    return False
            else:
                if metadata[key] != value:
                    return False
        return True

    def search_by_text(
        self,
        query_text: str,
        k: int,
        distance_measure: Callable = None,
        filter_metadata: Optional[Dict[str, Any]] = None,
        return_as_text: bool = False,
    ) -> List[Tuple[str, float, Dict[str, Any]]]:
        """Search by text query with optional metadata filtering."""
        query_vector = self.embedding_model.get_embedding(query_text)
        results = self.search(query_vector, k, distance_measure, filter_metadata)
        if return_as_text:
            return [result[0] for result in results]
        return results

    def search_by_text_with_measure(
        self,
        query_text: str,
        k: int,
        similarity_measure: str = "cosine",
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[Tuple[str, float, Dict[str, Any]]]:
        """
        Search by text using a named similarity measure.
        
        Args:
            query_text: The search query
            k: Number of results
            similarity_measure: One of 'cosine', 'euclidean', 'dot_product', 'manhattan', 'jaccard'
            filter_metadata: Optional metadata filters
        """
        measure_func = SIMILARITY_MEASURES.get(similarity_measure, cosine_similarity)
        return self.search_by_text(query_text, k, measure_func, filter_metadata)

    def retrieve_from_key(self, key: str) -> Tuple[Optional[np.ndarray], Optional[Dict[str, Any]]]:
        """Retrieve vector and metadata by key."""
        return self.vectors.get(key), self.metadata.get(key)

    def get_all_metadata_values(self, key: str) -> List[Any]:
        """Get all unique values for a metadata key."""
        values = set()
        for meta in self.metadata.values():
            if key in meta:
                values.add(meta[key])
        return list(values)

    async def abuild_from_list(
        self, 
        list_of_text: List[str],
        list_of_metadata: Optional[List[Dict[str, Any]]] = None
    ) -> "MetadataVectorDatabase":
        """Build database from list of texts asynchronously."""
        embeddings = await self.embedding_model.async_get_embeddings(list_of_text)
        
        for i, (text, embedding) in enumerate(zip(list_of_text, embeddings)):
            metadata = list_of_metadata[i] if list_of_metadata and i < len(list_of_metadata) else {}
            self.insert(text, embedding, metadata)
        
        return self
    
    def build_from_list(
        self, 
        list_of_text: List[str],
        list_of_metadata: Optional[List[Dict[str, Any]]] = None
    ) -> "MetadataVectorDatabase":
        """Synchronously build database from list of texts."""
        embeddings = self.embedding_model.get_embeddings(list_of_text)
        
        for i, (text, embedding) in enumerate(zip(list_of_text, embeddings)):
            metadata = list_of_metadata[i] if list_of_metadata and i < len(list_of_metadata) else {}
            self.insert(text, embedding, metadata)
        
        return self

    def save(self, filepath: str) -> None:
        """
        Save the vector database to a JSON file.
        
        Converts numpy arrays to lists for JSON serialization.
        
        Args:
            filepath: Path to save the database (should end with .json)
        """
        data = {
            "vectors": {
                key: _to_list(vector) for key, vector in self.vectors.items()
            },
            "metadata": self.metadata
        }
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else ".", exist_ok=True)
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"Saved vector database to {filepath} ({len(self.vectors)} vectors)")

    @classmethod
    def load(cls, filepath: str, embedding_model: EmbeddingModel = None) -> "MetadataVectorDatabase":
        """
        Load a vector database from a JSON file.
        
        Converts lists back to numpy arrays for efficient computation.
        
        Args:
            filepath: Path to the saved database
            embedding_model: Optional embedding model (only needed for new queries)
            
        Returns:
            Loaded MetadataVectorDatabase instance
        """
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        db = cls(embedding_model=embedding_model)
        
        for key, vector_list in data["vectors"].items():
            db.vectors[key] = np.array(vector_list, dtype=np.float32)
        
        db.metadata = data.get("metadata", {})
        
        print(f"Loaded vector database from {filepath} ({len(db.vectors)} vectors)")
        return db

    @classmethod
    def load_from_url(cls, url: str, embedding_model: EmbeddingModel = None) -> "MetadataVectorDatabase":
        """
        Load a vector database from a URL (e.g., GitHub raw, S3, Vercel Blob).
        
        Args:
            url: URL to the JSON database file
            embedding_model: Optional embedding model (only needed for new queries)
            
        Returns:
            Loaded MetadataVectorDatabase instance
        """
        print(f"Loading vector database from URL: {url}")
        
        try:
            with urllib.request.urlopen(url, timeout=60) as response:
                data = json.loads(response.read().decode("utf-8"))
        except urllib.error.URLError as e:
            raise RuntimeError(f"Failed to load vector database from URL: {e}")
        
        db = cls(embedding_model=embedding_model)
        
        for key, vector_list in data["vectors"].items():
            db.vectors[key] = np.array(vector_list, dtype=np.float32)
        
        db.metadata = data.get("metadata", {})
        
        print(f"Loaded vector database from URL ({len(db.vectors)} vectors)")
        return db

    @classmethod
    def load_auto(
        cls, 
        source: str, 
        embedding_model: EmbeddingModel = None
    ) -> "MetadataVectorDatabase":
        """
        Automatically load from file path or URL.
        
        Args:
            source: Either a local file path or a URL
            embedding_model: Optional embedding model
            
        Returns:
            Loaded MetadataVectorDatabase instance
        """
        if source.startswith(("http://", "https://")):
            return cls.load_from_url(source, embedding_model)
        else:
            return cls.load(source, embedding_model)

    def get_size(self) -> int:
        """Return the number of vectors in the database."""
        return len(self.vectors)


if __name__ == "__main__":
    # Example usage
    list_of_text = [
        "I like to eat broccoli and bananas.",
        "I ate a banana and spinach smoothie for breakfast.",
        "Chinchillas and kittens are cute.",
        "My sister adopted a kitten yesterday.",
        "Look at this cute hamster munching on a piece of broccoli.",
    ]

    vector_db = VectorDatabase()
    vector_db = asyncio.run(vector_db.abuild_from_list(list_of_text))
    k = 2

    searched_vector = vector_db.search_by_text("I think fruit is awesome!", k=k)
    print(f"Closest {k} vector(s):", searched_vector)

    retrieved_vector = vector_db.retrieve_from_key(
        "I like to eat broccoli and bananas."
    )
    print("Retrieved vector:", retrieved_vector)

    relevant_texts = vector_db.search_by_text(
        "I think fruit is awesome!", k=k, return_as_text=True
    )
    print(f"Closest {k} text(s):", relevant_texts)
