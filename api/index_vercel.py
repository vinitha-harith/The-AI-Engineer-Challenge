"""
Vercel-Optimized FastAPI Backend

This is a lightweight version optimized for Vercel's 250MB serverless function limit.
- No numpy dependency (uses pure Python vector operations)
- Loads vector database from GitHub URL
- Lazy initialization for serverless cold starts

For production deployments with numpy support, use index.py instead.
"""

import json
import math
import os
import urllib.request
from functools import lru_cache
from typing import Optional, List, Dict, Any, Tuple, Callable

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
from openai import OpenAI

from dotenv import load_dotenv
load_dotenv()


# ============ Configuration ============

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    openai_api_key: Optional[str] = None
    vector_db_url: str = "https://raw.githubusercontent.com/vinitha-harith/The-AI-Engineer-Challenge/main/vectorstore/vector_db.json"
    default_similarity_measure: str = "cosine"
    default_num_sources: int = 5
    chat_model: str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-3-small"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance."""
    return Settings()


# ============ Pure Python Vector Operations ============

def _dot_product(a: List[float], b: List[float]) -> float:
    """Pure Python dot product."""
    return sum(x * y for x, y in zip(a, b))


def _norm(a: List[float]) -> float:
    """Pure Python vector norm (L2)."""
    return math.sqrt(sum(x * x for x in a))


def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Cosine similarity between two vectors."""
    dot = _dot_product(a, b)
    norm_a = _norm(a)
    norm_b = _norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def euclidean_distance(a: List[float], b: List[float]) -> float:
    """Euclidean distance (negated for consistent sorting)."""
    diff = [x - y for x, y in zip(a, b)]
    return -_norm(diff)


def dot_product_similarity(a: List[float], b: List[float]) -> float:
    """Dot product similarity."""
    return _dot_product(a, b)


def manhattan_distance(a: List[float], b: List[float]) -> float:
    """Manhattan distance (negated for consistent sorting)."""
    return -sum(abs(x - y) for x, y in zip(a, b))


def jaccard_similarity(a: List[float], b: List[float]) -> float:
    """Jaccard-like similarity for continuous vectors."""
    min_sum = sum(min(abs(x), abs(y)) for x, y in zip(a, b))
    max_sum = sum(max(abs(x), abs(y)) for x, y in zip(a, b))
    if max_sum == 0:
        return 0.0
    return min_sum / max_sum


SIMILARITY_MEASURES = {
    "cosine": cosine_similarity,
    "euclidean": euclidean_distance,
    "dot_product": dot_product_similarity,
    "manhattan": manhattan_distance,
    "jaccard": jaccard_similarity,
}


# ============ Lightweight Vector Database ============

class LightweightVectorDB:
    """
    Pure Python vector database for Vercel deployment.
    No numpy dependency, loads from URL.
    """
    
    def __init__(self):
        self.vectors: Dict[str, List[float]] = {}
        self.metadata: Dict[str, Dict[str, Any]] = {}
        self._openai_client: Optional[OpenAI] = None
    
    @property
    def openai_client(self) -> OpenAI:
        if self._openai_client is None:
            self._openai_client = OpenAI()
        return self._openai_client
    
    def load_from_url(self, url: str) -> None:
        """Load vector database from a URL."""
        print(f"Loading vector database from: {url}")
        
        try:
            with urllib.request.urlopen(url, timeout=60) as response:
                data = json.loads(response.read().decode("utf-8"))
        except urllib.error.URLError as e:
            raise RuntimeError(f"Failed to load vector database: {e}")
        
        self.vectors = data.get("vectors", {})
        self.metadata = data.get("metadata", {})
        
        print(f"Loaded {len(self.vectors)} vectors")
    
    def get_embedding(self, text: str, model: str = "text-embedding-3-small") -> List[float]:
        """Get embedding for a text query."""
        response = self.openai_client.embeddings.create(
            input=text,
            model=model
        )
        return response.data[0].embedding
    
    def search(
        self,
        query: str,
        k: int = 5,
        similarity_fn: Callable = cosine_similarity,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[str, float, Dict[str, Any]]]:
        """
        Search for similar vectors.
        
        Returns list of (text, score, metadata) tuples.
        """
        query_embedding = self.get_embedding(query)
        
        results = []
        for key, vector in self.vectors.items():
            # Apply metadata filter
            if filter_metadata:
                meta = self.metadata.get(key, {})
                if not all(meta.get(k) == v for k, v in filter_metadata.items() if v is not None):
                    continue
            
            score = similarity_fn(query_embedding, vector)
            results.append((key, score, self.metadata.get(key, {})))
        
        # Sort by score (higher = more similar)
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:k]
    
    def get_size(self) -> int:
        return len(self.vectors)


# ============ RAG Pipeline ============

class VercelRAGPipeline:
    """Lightweight RAG pipeline for Vercel."""
    
    AVAILABLE_TOPICS = ["exercise", "nutrition", "sleep", "stress", "habits", "health"]
    AVAILABLE_DIFFICULTIES = ["beginner", "intermediate", "advanced"]
    
    SYSTEM_PROMPT = """You are a knowledgeable and supportive wellness coach. 
You provide helpful, accurate advice about health, fitness, nutrition, sleep, stress management, and building healthy habits.

Use the following context to answer the user's question. If the context doesn't contain relevant information, 
say so and provide general guidance based on your knowledge.

Context:
{context}

Guidelines:
- Be supportive and encouraging
- Provide specific, actionable advice when possible
- If recommending exercises or dietary changes, suggest consulting a healthcare provider for personalized advice
- Keep responses concise but comprehensive"""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.vector_db = LightweightVectorDB()
        self.is_initialized = False
    
    def initialize(self) -> None:
        """Initialize the pipeline by loading the vector database."""
        self.vector_db.load_from_url(self.settings.vector_db_url)
        self.is_initialized = True
    
    def retrieve(
        self,
        query: str,
        k: int = 5,
        similarity_measure: str = "cosine",
        filter_topic: Optional[str] = None,
        filter_difficulty: Optional[str] = None
    ) -> List[Tuple[str, float, Dict[str, Any]]]:
        """Retrieve relevant chunks."""
        similarity_fn = SIMILARITY_MEASURES.get(similarity_measure, cosine_similarity)
        
        filter_metadata = {}
        if filter_topic:
            filter_metadata["topic"] = filter_topic
        if filter_difficulty:
            filter_metadata["difficulty"] = filter_difficulty
        
        return self.vector_db.search(
            query, k, similarity_fn,
            filter_metadata if filter_metadata else None
        )
    
    def generate_response(
        self,
        query: str,
        k: int = 5,
        similarity_measure: str = "cosine",
        filter_topic: Optional[str] = None,
        filter_difficulty: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a RAG response."""
        # Retrieve context
        results = self.retrieve(query, k, similarity_measure, filter_topic, filter_difficulty)
        
        # Format context
        context_parts = []
        for i, (text, score, meta) in enumerate(results, 1):
            topic = meta.get("topic", "general")
            difficulty = meta.get("difficulty", "unknown")
            context_parts.append(f"[Source {i} - Topic: {topic}, Level: {difficulty}]\n{text}")
        context = "\n\n---\n\n".join(context_parts)
        
        # Generate response
        client = OpenAI()
        response = client.chat.completions.create(
            model=self.settings.chat_model,
            messages=[
                {"role": "system", "content": self.SYSTEM_PROMPT.format(context=context)},
                {"role": "user", "content": query}
            ]
        )
        
        # Format sources
        sources = [
            {
                "text": text[:200] + "..." if len(text) > 200 else text,
                "score": float(score),
                "topic": meta.get("topic"),
                "difficulty": meta.get("difficulty"),
                "source_file": meta.get("source")
            }
            for text, score, meta in results
        ]
        
        return {
            "response": response.choices[0].message.content,
            "sources": sources,
            "query": query,
            "similarity_measure": similarity_measure,
            "filters": {"topic": filter_topic, "difficulty": filter_difficulty}
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        topic_counts = {}
        difficulty_counts = {}
        
        for meta in self.vector_db.metadata.values():
            topic = meta.get("topic", "unknown")
            difficulty = meta.get("difficulty", "unknown")
            topic_counts[topic] = topic_counts.get(topic, 0) + 1
            difficulty_counts[difficulty] = difficulty_counts.get(difficulty, 0) + 1
        
        return {
            "total_chunks": self.vector_db.get_size(),
            "topics": topic_counts,
            "difficulty_levels": difficulty_counts,
            "similarity_measure": self.settings.default_similarity_measure,
            "vector_db_source": self.settings.vector_db_url
        }


# ============ Cached Pipeline ============

_cached_pipeline: Optional[VercelRAGPipeline] = None


def get_pipeline(settings: Settings = Depends(get_settings)) -> VercelRAGPipeline:
    """Get or create the RAG pipeline (lazy initialization)."""
    global _cached_pipeline
    
    if _cached_pipeline is None:
        print("🚀 Initializing Vercel RAG pipeline...")
        _cached_pipeline = VercelRAGPipeline(settings)
        _cached_pipeline.initialize()
        print(f"✅ Pipeline ready with {_cached_pipeline.vector_db.get_size()} vectors")
    
    return _cached_pipeline


# ============ FastAPI App ============

app = FastAPI(
    title="Wellness Coach API (Vercel)",
    description="Lightweight RAG-powered wellness coaching API optimized for Vercel",
    version="2.0.0-vercel"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)


# ============ Request/Response Models ============

class ChatRequest(BaseModel):
    message: str = Field(..., description="The user's message/question")
    topic: Optional[str] = Field(None, description="Filter by topic")
    difficulty: Optional[str] = Field(None, description="Filter by difficulty level")
    similarity_measure: Optional[str] = Field("cosine", description="Similarity measure")
    num_sources: Optional[int] = Field(5, ge=1, le=10, description="Number of sources")


class ChatResponse(BaseModel):
    reply: str
    sources: List[Dict[str, Any]]
    query: str
    similarity_measure: str
    filters: Dict[str, Optional[str]]


class HealthResponse(BaseModel):
    status: str
    openai_configured: bool
    pipeline_status: str
    vector_count: int
    runtime: str = "vercel-optimized"


# ============ Endpoints ============

@app.get("/")
def root():
    return {"status": "ok", "service": "wellness-coach-api", "version": "2.0.0-vercel"}


@app.get("/api/health", response_model=HealthResponse)
def health(settings: Settings = Depends(get_settings)):
    global _cached_pipeline
    
    return HealthResponse(
        status="healthy" if _cached_pipeline else "degraded",
        openai_configured=bool(settings.openai_api_key or os.getenv("OPENAI_API_KEY")),
        pipeline_status="initialized" if _cached_pipeline else "not_initialized",
        vector_count=_cached_pipeline.vector_db.get_size() if _cached_pipeline else 0
    )


@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest, pipeline: VercelRAGPipeline = Depends(get_pipeline)):
    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY not configured")
    
    # Validate inputs
    if request.topic and request.topic not in pipeline.AVAILABLE_TOPICS:
        raise HTTPException(status_code=400, detail=f"Invalid topic. Must be one of: {pipeline.AVAILABLE_TOPICS}")
    
    if request.difficulty and request.difficulty not in pipeline.AVAILABLE_DIFFICULTIES:
        raise HTTPException(status_code=400, detail=f"Invalid difficulty. Must be one of: {pipeline.AVAILABLE_DIFFICULTIES}")
    
    if request.similarity_measure and request.similarity_measure not in SIMILARITY_MEASURES:
        raise HTTPException(status_code=400, detail=f"Invalid similarity measure. Must be one of: {list(SIMILARITY_MEASURES.keys())}")
    
    try:
        result = pipeline.generate_response(
            query=request.message,
            k=request.num_sources or 5,
            similarity_measure=request.similarity_measure or "cosine",
            filter_topic=request.topic,
            filter_difficulty=request.difficulty
        )
        
        return ChatResponse(
            reply=result["response"],
            sources=result["sources"],
            query=result["query"],
            similarity_measure=result["similarity_measure"],
            filters=result["filters"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.get("/api/stats")
def stats(pipeline: VercelRAGPipeline = Depends(get_pipeline)):
    return pipeline.get_stats()


@app.get("/api/config")
def config():
    return {
        "available_topics": VercelRAGPipeline.AVAILABLE_TOPICS,
        "available_difficulties": VercelRAGPipeline.AVAILABLE_DIFFICULTIES,
        "available_similarity_measures": list(SIMILARITY_MEASURES.keys())
    }


@app.post("/api/retrieve")
def retrieve(request: ChatRequest, pipeline: VercelRAGPipeline = Depends(get_pipeline)):
    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY not configured")
    
    try:
        results = pipeline.retrieve(
            query=request.message,
            k=request.num_sources or 5,
            similarity_measure=request.similarity_measure or "cosine",
            filter_topic=request.topic,
            filter_difficulty=request.difficulty
        )
        
        return {
            "query": request.message,
            "results": [
                {"text": text, "score": float(score), "metadata": meta}
                for text, score, meta in results
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
