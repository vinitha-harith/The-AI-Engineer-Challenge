"""
FastAPI Backend with RAG Retrieval

Production-grade implementation using:
- Lifespan context manager for initialization/cleanup
- Application state for storing the pipeline
- Dependency injection for accessing the pipeline in routes

Prerequisites:
    Run 'python -m api.embed' to create the vector database before starting the server.
"""

from contextlib import asynccontextmanager
from functools import lru_cache
from pathlib import Path
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
import os

from dotenv import load_dotenv
load_dotenv()


# ============ Configuration ============

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    openai_api_key: Optional[str] = None
    vector_db_path: str = str(Path(__file__).parent.parent / "vectorstore" / "vector_db.json")
    default_similarity_measure: str = "cosine"
    default_num_sources: int = 5
    chat_model: str = "gpt-4o-mini"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance - loaded once and reused."""
    return Settings()


# ============ Lifespan Management ============

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    
    - Initializes the retrieval pipeline on startup
    - Stores it in app.state for access by routes
    - Cleans up resources on shutdown
    """
    settings = get_settings()
    
    # Startup: Initialize the retrieval pipeline
    print("🚀 Starting up Wellness Coach API...")
    
    try:
        from api.rag import RetrievalPipeline
        
        pipeline = RetrievalPipeline(
            vector_db_path=settings.vector_db_path,
            similarity_measure=settings.default_similarity_measure,
            chat_model=settings.chat_model
        )
        pipeline.initialize()
        
        # Store in app state
        app.state.pipeline = pipeline
        app.state.is_healthy = True
        
        print(f"✅ Pipeline initialized with {pipeline.vector_db.get_size()} vectors")
        
    except FileNotFoundError as e:
        print(f"⚠️  Vector database not found: {e}")
        print("   Run 'python -m api.embed' to create it.")
        app.state.pipeline = None
        app.state.is_healthy = False
        
    except Exception as e:
        print(f"❌ Failed to initialize pipeline: {e}")
        app.state.pipeline = None
        app.state.is_healthy = False
    
    yield  # Application runs here
    
    # Shutdown: Cleanup resources
    print("👋 Shutting down Wellness Coach API...")
    app.state.pipeline = None


# ============ Application Factory ============

def create_app() -> FastAPI:
    """Application factory for creating the FastAPI app."""
    
    app = FastAPI(
        title="Wellness Coach API",
        description="RAG-powered wellness coaching API with topic filtering and multiple similarity measures",
        version="2.0.0",
        lifespan=lifespan
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"]
    )
    
    return app


app = create_app()


# ============ Dependencies ============

def get_pipeline(request: Request):
    """
    Dependency injection for the retrieval pipeline.
    
    Retrieves the pipeline from app.state (initialized at startup).
    Raises 503 if the pipeline is not available.
    """
    pipeline = request.app.state.pipeline
    
    if pipeline is None:
        raise HTTPException(
            status_code=503,
            detail="Service unavailable. Vector database not initialized. "
                   "Run 'python -m api.embed' to create the database."
        )
    
    return pipeline


def require_api_key(settings: Settings = Depends(get_settings)):
    """Dependency to ensure OpenAI API key is configured."""
    if not settings.openai_api_key and not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(
            status_code=500,
            detail="OPENAI_API_KEY not configured"
        )
    return True


# ============ Request/Response Models ============

class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str = Field(..., description="The user's message/question")
    topic: Optional[str] = Field(None, description="Filter by topic (exercise, nutrition, sleep, stress, habits, health)")
    difficulty: Optional[str] = Field(None, description="Filter by difficulty level (beginner, intermediate, advanced)")
    similarity_measure: Optional[str] = Field("cosine", description="Similarity measure to use (cosine, euclidean, dot_product, manhattan, jaccard)")
    num_sources: Optional[int] = Field(5, ge=1, le=10, description="Number of source chunks to retrieve")


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    reply: str
    sources: List[Dict[str, Any]]
    query: str
    similarity_measure: str
    filters: Dict[str, Optional[str]]


class StatsResponse(BaseModel):
    """Response model for stats endpoint."""
    total_chunks: int
    topics: Dict[str, int]
    difficulty_levels: Dict[str, int]
    similarity_measure: str
    vector_db_path: str


class ConfigResponse(BaseModel):
    """Response model for configuration endpoint."""
    available_topics: List[str]
    available_difficulties: List[str]
    available_similarity_measures: List[str]


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    openai_configured: bool
    pipeline_status: str
    vector_count: int


# ============ Endpoints ============

@app.get("/")
def root():
    """Health check endpoint."""
    return {"status": "ok", "service": "wellness-coach-api", "version": "2.0.0"}


@app.get("/api/health", response_model=HealthResponse)
def health(request: Request, settings: Settings = Depends(get_settings)):
    """Detailed health check."""
    pipeline = request.app.state.pipeline
    
    if pipeline is None:
        return HealthResponse(
            status="degraded",
            openai_configured=bool(settings.openai_api_key or os.getenv("OPENAI_API_KEY")),
            pipeline_status="not_initialized",
            vector_count=0
        )
    
    return HealthResponse(
        status="healthy",
        openai_configured=bool(settings.openai_api_key or os.getenv("OPENAI_API_KEY")),
        pipeline_status="initialized",
        vector_count=pipeline.vector_db.get_size() if pipeline.vector_db else 0
    )


@app.post("/api/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    pipeline = Depends(get_pipeline),
    _api_key: bool = Depends(require_api_key)
):
    """
    Chat endpoint with RAG-powered responses.
    
    Retrieves relevant context from the pre-built vector database 
    and generates a response using the specified filters and similarity measure.
    """
    # Validate filters
    valid_topics = pipeline.get_available_topics()
    valid_difficulties = pipeline.get_available_difficulties()
    valid_measures = pipeline.get_available_similarity_measures()
    
    if request.topic and request.topic not in valid_topics:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid topic. Must be one of: {valid_topics}"
        )
    
    if request.difficulty and request.difficulty not in valid_difficulties:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid difficulty. Must be one of: {valid_difficulties}"
        )
    
    if request.similarity_measure and request.similarity_measure not in valid_measures:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid similarity measure. Must be one of: {valid_measures}"
        )
    
    try:
        result = pipeline.generate_response(
            query=request.message,
            k=request.num_sources or 5,
            similarity_measure=request.similarity_measure,
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
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


@app.get("/api/stats", response_model=StatsResponse)
def stats(pipeline = Depends(get_pipeline)):
    """Get statistics about the loaded knowledge base."""
    stats_data = pipeline.get_stats()
    
    if "error" in stats_data:
        raise HTTPException(status_code=500, detail=stats_data["error"])
    
    return StatsResponse(**stats_data)


@app.get("/api/config", response_model=ConfigResponse)
def config(request: Request):
    """Get available configuration options."""
    pipeline = request.app.state.pipeline
    
    if pipeline:
        return ConfigResponse(
            available_topics=pipeline.get_available_topics(),
            available_difficulties=pipeline.get_available_difficulties(),
            available_similarity_measures=pipeline.get_available_similarity_measures()
        )
    
    # Return defaults even if database not loaded
    from api.rag import AVAILABLE_TOPICS, AVAILABLE_DIFFICULTIES, AVAILABLE_SIMILARITY_MEASURES
    return ConfigResponse(
        available_topics=AVAILABLE_TOPICS,
        available_difficulties=AVAILABLE_DIFFICULTIES,
        available_similarity_measures=AVAILABLE_SIMILARITY_MEASURES
    )


@app.post("/api/retrieve")
def retrieve(
    request: ChatRequest,
    pipeline = Depends(get_pipeline),
    _api_key: bool = Depends(require_api_key)
):
    """
    Retrieve relevant chunks without generating a response.
    Useful for debugging or building custom responses.
    """
    try:
        results = pipeline.retrieve(
            query=request.message,
            k=request.num_sources or 5,
            similarity_measure=request.similarity_measure,
            filter_topic=request.topic,
            filter_difficulty=request.difficulty
        )
        
        return {
            "query": request.message,
            "results": [
                {
                    "text": text,
                    "score": float(score),
                    "metadata": meta
                }
                for text, score, meta in results
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving: {str(e)}")


# For Vercel serverless deployment
# The app object is used directly by Vercel's Python runtime
