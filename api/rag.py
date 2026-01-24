"""
RAG Retrieval Module - Query the pre-built vector database.

This module loads a pre-built vector database (created by embed.py) and provides:
- Semantic search with multiple similarity measures
- Metadata-based filtering (topic, difficulty)
- Context-aware response generation

Usage:
    First, build the vector database:
        python -m api.embed
    
    Then use this module for retrieval:
        from api.rag import get_retrieval_pipeline
        pipeline = get_retrieval_pipeline()
        response = pipeline.generate_response("How can I sleep better?")
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from aimakerspace.vectordatabase import (
    MetadataVectorDatabase, 
    SIMILARITY_MEASURES,
    cosine_similarity
)
from aimakerspace.openai_utils.embedding import EmbeddingModel
from aimakerspace.openai_utils.chatmodel import ChatOpenAI
from aimakerspace.openai_utils.prompts import SystemRolePrompt, UserRolePrompt


# ============ Available Options ============

AVAILABLE_TOPICS = ["exercise", "nutrition", "sleep", "stress", "habits", "health"]
AVAILABLE_DIFFICULTIES = ["beginner", "intermediate", "advanced"]
AVAILABLE_SIMILARITY_MEASURES = list(SIMILARITY_MEASURES.keys())


# ============ Retrieval Pipeline ============

class RetrievalPipeline:
    """
    Retrieval pipeline that loads a pre-built vector database
    and provides semantic search and response generation.
    
    This is decoupled from the embedding process (see embed.py).
    """
    
    def __init__(
        self,
        vector_db_path: str,
        similarity_measure: str = "cosine",
        chat_model: str = "gpt-4o-mini"
    ):
        self.vector_db_path = vector_db_path
        self.similarity_measure = similarity_measure
        self.chat_model_name = chat_model
        
        self.vector_db: Optional[MetadataVectorDatabase] = None
        self.embedding_model: Optional[EmbeddingModel] = None
        self.is_initialized = False
        
        # Prompts for RAG
        self.system_prompt = SystemRolePrompt(
            """You are a knowledgeable and supportive wellness coach. 
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
        )
        
        self.user_prompt = UserRolePrompt("{question}")

    def initialize(self) -> None:
        """Load the pre-built vector database."""
        if not os.path.exists(self.vector_db_path):
            raise FileNotFoundError(
                f"Vector database not found at: {self.vector_db_path}\n"
                f"Please run 'python -m api.embed' first to create the database."
            )
        
        # Create embedding model for query embedding
        self.embedding_model = EmbeddingModel()
        
        # Load the pre-built vector database
        self.vector_db = MetadataVectorDatabase.load(
            self.vector_db_path, 
            embedding_model=self.embedding_model
        )
        
        self.is_initialized = True
        print(f"Retrieval pipeline initialized with {self.vector_db.get_size()} vectors")

    def retrieve(
        self,
        query: str,
        k: int = 5,
        similarity_measure: Optional[str] = None,
        filter_topic: Optional[str] = None,
        filter_difficulty: Optional[str] = None
    ) -> List[Tuple[str, float, Dict[str, Any]]]:
        """
        Retrieve relevant chunks for a query.
        
        Args:
            query: The search query
            k: Number of results to return
            similarity_measure: Override default similarity measure
            filter_topic: Filter by topic category
            filter_difficulty: Filter by difficulty level
            
        Returns:
            List of (chunk_text, score, metadata) tuples
        """
        if not self.is_initialized or self.vector_db is None:
            raise RuntimeError(
                "Retrieval pipeline not initialized. Call initialize() first."
            )
        
        measure = similarity_measure or self.similarity_measure
        
        # Build filter metadata
        filter_metadata = {}
        if filter_topic:
            filter_metadata["topic"] = filter_topic
        if filter_difficulty:
            filter_metadata["difficulty"] = filter_difficulty
        
        filter_metadata = filter_metadata if filter_metadata else None
        
        return self.vector_db.search_by_text_with_measure(
            query, k, measure, filter_metadata
        )

    def format_context(self, results: List[Tuple[str, float, Dict[str, Any]]]) -> str:
        """Format retrieved results into context string."""
        context_parts = []
        for i, (text, score, metadata) in enumerate(results, 1):
            topic = metadata.get("topic", "general")
            difficulty = metadata.get("difficulty", "unknown")
            context_parts.append(
                f"[Source {i} - Topic: {topic}, Level: {difficulty}]\n{text}"
            )
        return "\n\n---\n\n".join(context_parts)

    def generate_response(
        self,
        query: str,
        k: int = 5,
        similarity_measure: Optional[str] = None,
        filter_topic: Optional[str] = None,
        filter_difficulty: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a response using RAG.
        
        Returns:
            Dict with 'response', 'sources', and 'metadata'
        """
        # Retrieve relevant chunks
        results = self.retrieve(
            query, k, similarity_measure, filter_topic, filter_difficulty
        )
        
        # Format context
        context = self.format_context(results)
        
        # Generate response using chat model
        chat_model = ChatOpenAI(model_name=self.chat_model_name)
        
        messages = [
            self.system_prompt.create_message(context=context),
            self.user_prompt.create_message(question=query)
        ]
        
        response = chat_model.run(messages)
        
        # Extract source information
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
            "response": response,
            "sources": sources,
            "query": query,
            "similarity_measure": similarity_measure or self.similarity_measure,
            "filters": {
                "topic": filter_topic,
                "difficulty": filter_difficulty
            }
        }

    def get_available_topics(self) -> List[str]:
        """Get list of available topic categories."""
        return AVAILABLE_TOPICS

    def get_available_difficulties(self) -> List[str]:
        """Get list of available difficulty levels."""
        return AVAILABLE_DIFFICULTIES

    def get_available_similarity_measures(self) -> List[str]:
        """Get list of available similarity measures."""
        return AVAILABLE_SIMILARITY_MEASURES

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the loaded database."""
        if not self.is_initialized or self.vector_db is None:
            return {"error": "Pipeline not initialized"}
        
        # Count topics and difficulties from metadata
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
            "similarity_measure": self.similarity_measure,
            "vector_db_path": self.vector_db_path
        }


# ============ Pipeline Factory ============

from functools import lru_cache


@lru_cache(maxsize=1)
def get_retrieval_pipeline(
    vector_db_path: Optional[str] = None
) -> RetrievalPipeline:
    """
    Get or initialize the retrieval pipeline.
    
    Uses lru_cache for efficient caching without global state.
    The cache is keyed by vector_db_path, so different paths
    create different cached instances.
    
    Args:
        vector_db_path: Path to the vector database JSON file
        
    Returns:
        Initialized RetrievalPipeline instance
    """
    # Default path
    if vector_db_path is None:
        api_dir = Path(__file__).parent
        vector_db_path = str(api_dir.parent / "vectorstore" / "vector_db.json")
    
    pipeline = RetrievalPipeline(vector_db_path=vector_db_path)
    pipeline.initialize()
    
    return pipeline


def clear_pipeline_cache() -> None:
    """Clear the cached pipeline instance. Useful for testing or reloading."""
    get_retrieval_pipeline.cache_clear()


# ============ Convenience Functions ============

def retrieve(
    query: str,
    k: int = 5,
    similarity_measure: str = "cosine",
    filter_topic: Optional[str] = None,
    filter_difficulty: Optional[str] = None
) -> List[Tuple[str, float, Dict[str, Any]]]:
    """
    Convenience function to retrieve relevant chunks.
    
    Automatically initializes the pipeline if needed.
    """
    pipeline = get_retrieval_pipeline()
    return pipeline.retrieve(query, k, similarity_measure, filter_topic, filter_difficulty)


def generate_response(
    query: str,
    k: int = 5,
    similarity_measure: str = "cosine",
    filter_topic: Optional[str] = None,
    filter_difficulty: Optional[str] = None
) -> Dict[str, Any]:
    """
    Convenience function to generate a RAG response.
    
    Automatically initializes the pipeline if needed.
    """
    pipeline = get_retrieval_pipeline()
    return pipeline.generate_response(query, k, similarity_measure, filter_topic, filter_difficulty)


# ============ Main (for testing) ============

if __name__ == "__main__":
    print("Testing Retrieval Pipeline...")
    print("-" * 50)
    
    try:
        pipeline = get_retrieval_pipeline()
        
        print("\n📊 Database Stats:")
        stats = pipeline.get_stats()
        for key, value in stats.items():
            print(f"   {key}: {value}")
        
        print("\n🔍 Test Retrieval:")
        results = pipeline.retrieve("How can I improve my sleep?", k=3)
        for i, (text, score, meta) in enumerate(results, 1):
            print(f"\n   {i}. Score: {score:.4f}")
            print(f"      Topic: {meta.get('topic')}, Difficulty: {meta.get('difficulty')}")
            print(f"      Preview: {text[:80]}...")
        
        print("\n✅ Retrieval pipeline test successful!")
        
    except FileNotFoundError as e:
        print(f"\n⚠️  {e}")
        print("\nTo create the vector database, run:")
        print("   python -m api.embed")
