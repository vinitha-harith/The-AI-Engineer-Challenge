import json
import os
import math
import urllib.request
from collections import defaultdict
from typing import List, Tuple, Callable, Dict, Any, Optional, Union
from aimakerspace.openai_utils.embedding import EmbeddingModel
import asyncio

# Try to import numpy, fall back to pure Python if not available
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


# ============ Pure Python Vector Operations ============

def _dot_product_py(a: List[float], b: List[float]) -> float:
    """Pure Python dot product."""
    return sum(x * y for x, y in zip(a, b))


def _norm_py(a: List[float]) -> float:
    """Pure Python vector norm (L2)."""
    return math.sqrt(sum(x * x for x in a))


def _subtract_py(a: List[float], b: List[float]) -> List[float]:
    """Pure Python vector subtraction."""
    return [x - y for x, y in zip(a, b)]


# ============ Similarity Measures ============

def cosine_similarity(vector_a, vector_b) -> float:
    """Computes the cosine similarity between two vectors."""
    if HAS_NUMPY:
        dot_product = np.dot(vector_a, vector_b)
        norm_a = np.linalg.norm(vector_a)
        norm_b = np.linalg.norm(vector_b)
    else:
        # Pure Python fallback
        a = list(vector_a) if not isinstance(vector_a, list) else vector_a
        b = list(vector_b) if not isinstance(vector_b, list) else vector_b
        dot_product = _dot_product_py(a, b)
        norm_a = _norm_py(a)
        norm_b = _norm_py(b)
    
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot_product / (norm_a * norm_b)


def euclidean_distance(vector_a, vector_b) -> float:
    """
    Computes the euclidean distance between two vectors.
    Returns negative distance so higher values = more similar (for consistent sorting).
    """
    if HAS_NUMPY:
        distance = np.linalg.norm(vector_a - vector_b)
    else:
        a = list(vector_a) if not isinstance(vector_a, list) else vector_a
        b = list(vector_b) if not isinstance(vector_b, list) else vector_b
        diff = _subtract_py(a, b)
        distance = _norm_py(diff)
    return -distance  # Negative so higher = more similar


def dot_product_similarity(vector_a, vector_b) -> float:
    """Computes the dot product between two vectors."""
    if HAS_NUMPY:
        return float(np.dot(vector_a, vector_b))
    else:
        a = list(vector_a) if not isinstance(vector_a, list) else vector_a
        b = list(vector_b) if not isinstance(vector_b, list) else vector_b
        return _dot_product_py(a, b)


def manhattan_distance(vector_a, vector_b) -> float:
    """
    Computes the Manhattan (L1) distance between two vectors.
    Returns negative distance so higher values = more similar.
    """
    if HAS_NUMPY:
        distance = np.sum(np.abs(vector_a - vector_b))
    else:
        a = list(vector_a) if not isinstance(vector_a, list) else vector_a
        b = list(vector_b) if not isinstance(vector_b, list) else vector_b
        distance = sum(abs(x - y) for x, y in zip(a, b))
    return -distance


def jaccard_similarity(vector_a, vector_b) -> float:
    """
    Computes Jaccard-like similarity for continuous vectors.
    Uses the ratio of minimum to maximum values element-wise.
    """
    if HAS_NUMPY:
        min_sum = np.sum(np.minimum(np.abs(vector_a), np.abs(vector_b)))
        max_sum = np.sum(np.maximum(np.abs(vector_a), np.abs(vector_b)))
    else:
        a = list(vector_a) if not isinstance(vector_a, list) else vector_a
        b = list(vector_b) if not isinstance(vector_b, list) else vector_b
        min_sum = sum(min(abs(x), abs(y)) for x, y in zip(a, b))
        max_sum = sum(max(abs(x), abs(y)) for x, y in zip(a, b))
    
    if max_sum == 0:
        return 0.0
    return min_sum / max_sum


# Map of similarity measure names to functions
SIMILARITY_MEASURES = {
    "cosine": cosine_similarity,
    "euclidean": euclidean_distance,
    "dot_product": dot_product_similarity,
    "manhattan": manhattan_distance,
    "jaccard": jaccard_similarity,
}


def _to_vector(data) -> List[float]:
    """Convert numpy array or list to list of floats."""
    if HAS_NUMPY:
        import numpy as np
        if isinstance(data, np.ndarray):
            return data.tolist()
    if hasattr(data, 'tolist'):
        return data.tolist()
    return list(data)


class VectorDatabase:
    def __init__(self, embedding_model: EmbeddingModel = None):
        self.vectors = defaultdict(list)
        self.embedding_model = embedding_model or EmbeddingModel()

    def insert(self, key: str, vector) -> None:
        self.vectors[key] = _to_vector(vector)

    def search(
        self,
        query_vector,
        k: int,
        distance_measure: Callable = cosine_similarity,
    ) -> List[Tuple[str, float]]:
        scores = [
            (key, distance_measure(query_vector, vector))
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
        query_vector = self.embedding_model.get_embedding(query_text)
        results = self.search(query_vector, k, distance_measure)
        return [result[0] for result in results] if return_as_text else results

    def retrieve_from_key(self, key: str):
        return self.vectors.get(key, None)

    async def abuild_from_list(self, list_of_text: List[str]) -> "VectorDatabase":
        embeddings = await self.embedding_model.async_get_embeddings(list_of_text)
        for text, embedding in zip(list_of_text, embeddings):
            self.insert(text, embedding)
        return self


class MetadataVectorDatabase:
    """
    Enhanced Vector Database with metadata support for filtering.
    
    Supports:
    - Topic categories (exercise, nutrition, sleep, stress, habits, health)
    - Difficulty levels (beginner, intermediate, advanced)
    - Source file tracking
    - Multiple similarity measures
    - Pure Python fallback when numpy is not available
    """
    
    def __init__(self, embedding_model: EmbeddingModel = None):
        self.vectors: Dict[str, List[float]] = {}
        self.metadata: Dict[str, Dict[str, Any]] = {}
        self.embedding_model = embedding_model or EmbeddingModel()
        self.default_similarity = cosine_similarity

    def insert(
        self, 
        key: str, 
        vector, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Insert a vector with optional metadata."""
        self.vectors[key] = _to_vector(vector)
        self.metadata[key] = metadata or {}

    def search(
        self,
        query_vector,
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
        
        # Filter vectors by metadata if specified
        filtered_keys = self.vectors.keys()
        if filter_metadata:
            filtered_keys = [
                key for key in filtered_keys
                if self._matches_filter(self.metadata.get(key, {}), filter_metadata)
            ]
        
        # Calculate scores
        scores = [
            (key, distance_measure(query_vector, self.vectors[key]), self.metadata.get(key, {}))
            for key in filtered_keys
        ]
        
        return sorted(scores, key=lambda x: x[1], reverse=True)[:k]

    def _matches_filter(self, metadata: Dict[str, Any], filter_metadata: Dict[str, Any]) -> bool:
        """Check if metadata matches the filter criteria."""
        for key, value in filter_metadata.items():
            if key not in metadata:
                return False
            if isinstance(value, list):
                # If filter value is a list, check if metadata value is in the list
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

    def retrieve_from_key(self, key: str) -> Tuple[Optional[List[float]], Optional[Dict[str, Any]]]:
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
        """Build database from list of texts with optional metadata."""
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
        """Synchronously build database from list of texts with optional metadata."""
        embeddings = self.embedding_model.get_embeddings(list_of_text)
        
        for i, (text, embedding) in enumerate(zip(list_of_text, embeddings)):
            metadata = list_of_metadata[i] if list_of_metadata and i < len(list_of_metadata) else {}
            self.insert(text, embedding, metadata)
        
        return self

    def save(self, filepath: str) -> None:
        """
        Save the vector database to a JSON file.
        
        Args:
            filepath: Path to save the database (should end with .json)
        """
        data = {
            "vectors": {
                key: _to_vector(vector) for key, vector in self.vectors.items()
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
            # Store as list (pure Python compatible)
            db.vectors[key] = vector_list
        
        db.metadata = data.get("metadata", {})
        
        print(f"Loaded vector database from {filepath} ({len(db.vectors)} vectors)")
        return db

    @classmethod
    def load_from_url(cls, url: str, embedding_model: EmbeddingModel = None) -> "MetadataVectorDatabase":
        """
        Load a vector database from a URL (e.g., GitHub raw, Vercel Blob, S3).
        
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
            # Store as list (pure Python compatible)
            db.vectors[key] = vector_list
        
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
