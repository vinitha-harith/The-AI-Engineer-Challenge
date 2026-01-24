#!/usr/bin/env python3
"""
Embedding Script - Creates and persists the vector database.

This script is run ONCE (or whenever data changes) to:
1. Load all documents from the data directory
2. Split documents into chunks with metadata
3. Generate embeddings via OpenAI API
4. Save the vector database to disk

Usage:
    python -m api.embed
    
    Or with custom paths:
    python -m api.embed --data-dir ./data --output ./vectorstore/db.json

The retrieval service (rag.py) will load the pre-built database.
"""

import os
import sys
import argparse
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Tuple

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from aimakerspace.text_utils import DirectoryLoader, CharacterTextSplitter
from aimakerspace.vectordatabase import MetadataVectorDatabase
from aimakerspace.openai_utils.embedding import EmbeddingModel


# ============ Topic and Difficulty Classification ============

TOPIC_KEYWORDS = {
    "exercise": [
        "exercise", "workout", "fitness", "cardio", "strength", "training",
        "stretching", "yoga", "movement", "physical", "muscle", "aerobic",
        "walking", "running", "cycling", "swimming", "squats", "push-ups",
        "planks", "flexibility", "balance", "back pain", "neck", "shoulder",
        "posture", "repetitions", "sets", "reps"
    ],
    "nutrition": [
        "nutrition", "diet", "food", "eating", "meal", "calories", "protein",
        "carbohydrates", "fats", "vitamins", "minerals", "healthy eating",
        "breakfast", "lunch", "dinner", "snack", "hydration", "water",
        "fruits", "vegetables", "fiber", "macronutrients", "micronutrients",
        "cooking", "recipe", "supplement"
    ],
    "sleep": [
        "sleep", "insomnia", "bedtime", "rest", "tired", "fatigue", "nap",
        "circadian", "rem", "dreams", "mattress", "pillow", "bedroom",
        "sleep hygiene", "melatonin", "drowsy", "awake", "wake up",
        "night", "recovery", "relaxation"
    ],
    "stress": [
        "stress", "anxiety", "mental health", "relaxation", "meditation",
        "mindfulness", "breathing", "calm", "worry", "overwhelm", "tension",
        "depression", "mood", "emotional", "therapy", "coping", "resilience",
        "burnout", "pressure", "grounding"
    ],
    "habits": [
        "habit", "routine", "morning", "evening", "schedule", "productivity",
        "goal", "motivation", "discipline", "consistency", "tracking",
        "behavior", "change", "pattern", "daily", "weekly", "lifestyle",
        "time management", "work-life balance"
    ],
    "health": [
        "health", "wellness", "immune", "digestion", "headache", "pain",
        "illness", "prevention", "medical", "symptoms", "treatment",
        "doctor", "disease", "chronic", "acute", "inflammation", "gut",
        "microbiome", "healing", "recovery"
    ]
}

DIFFICULTY_KEYWORDS = {
    "beginner": [
        "beginner", "basic", "simple", "easy", "start", "introduction",
        "fundamental", "first step", "getting started", "new to", "101"
    ],
    "intermediate": [
        "intermediate", "moderate", "some experience", "building on",
        "progressing", "developing", "improving", "enhancing"
    ],
    "advanced": [
        "advanced", "expert", "complex", "challenging", "intensive",
        "professional", "mastery", "optimization", "fine-tuning"
    ]
}


def classify_topic(text: str) -> str:
    """Classify text into a topic category based on keyword matching."""
    text_lower = text.lower()
    topic_scores = {}
    
    for topic, keywords in TOPIC_KEYWORDS.items():
        score = sum(1 for keyword in keywords if keyword in text_lower)
        topic_scores[topic] = score
    
    best_topic = max(topic_scores, key=topic_scores.get)
    return best_topic if topic_scores[best_topic] > 0 else "health"


def classify_difficulty(text: str) -> str:
    """Classify text into a difficulty level based on keyword matching."""
    text_lower = text.lower()
    difficulty_scores = {}
    
    for level, keywords in DIFFICULTY_KEYWORDS.items():
        score = sum(1 for keyword in keywords if keyword in text_lower)
        difficulty_scores[level] = score
    
    best_level = max(difficulty_scores, key=difficulty_scores.get)
    return best_level if difficulty_scores[best_level] > 0 else "beginner"


def extract_metadata(text: str, source: str = "") -> Dict[str, Any]:
    """Extract metadata from a text chunk."""
    return {
        "topic": classify_topic(text),
        "difficulty": classify_difficulty(text),
        "source": source,
        "char_count": len(text),
        "word_count": len(text.split())
    }


# ============ Main Embedding Pipeline ============

class EmbeddingPipeline:
    """
    Pipeline for creating and persisting the vector database.
    
    This is separate from the retrieval pipeline and should be run
    whenever the source data changes.
    """
    
    def __init__(
        self,
        data_directory: str,
        output_path: str,
        chunk_size: int = 500,
        chunk_overlap: int = 100
    ):
        self.data_directory = data_directory
        self.output_path = output_path
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        self.documents: List[str] = []
        self.doc_sources: List[str] = []
        self.chunks: List[str] = []
        self.chunk_metadata: List[Dict[str, Any]] = []

    def load_documents(self) -> int:
        """Load all documents from the data directory."""
        print(f"\n📂 Loading documents from: {self.data_directory}")
        
        loader = DirectoryLoader(self.data_directory)
        docs_with_meta = loader.load_documents_with_metadata()
        
        self.documents = []
        self.doc_sources = []
        
        for doc, meta in docs_with_meta:
            self.documents.append(doc)
            source = meta.get("source", "unknown")
            self.doc_sources.append(source)
            print(f"   ✓ Loaded: {os.path.basename(source)} ({len(doc)} chars)")
        
        print(f"   Total: {len(self.documents)} documents")
        return len(self.documents)

    def split_documents(self) -> int:
        """Split documents into chunks with metadata."""
        print(f"\n✂️  Splitting documents (chunk_size={self.chunk_size}, overlap={self.chunk_overlap})")
        
        splitter = CharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap
        )
        
        self.chunks = []
        self.chunk_metadata = []
        
        for doc_idx, doc in enumerate(self.documents):
            source = self.doc_sources[doc_idx] if doc_idx < len(self.doc_sources) else "unknown"
            doc_chunks = splitter.split(doc)
            
            for chunk in doc_chunks:
                if chunk.strip():
                    self.chunks.append(chunk)
                    metadata = extract_metadata(chunk, source)
                    self.chunk_metadata.append(metadata)
        
        # Print topic distribution
        topic_counts = {}
        for meta in self.chunk_metadata:
            topic = meta.get("topic", "unknown")
            topic_counts[topic] = topic_counts.get(topic, 0) + 1
        
        print(f"   Total chunks: {len(self.chunks)}")
        print(f"   Topic distribution:")
        for topic, count in sorted(topic_counts.items()):
            print(f"      - {topic}: {count}")
        
        return len(self.chunks)

    def create_embeddings(self) -> MetadataVectorDatabase:
        """Generate embeddings and build the vector database."""
        print(f"\n🔢 Generating embeddings for {len(self.chunks)} chunks...")
        print("   (This may take a moment and uses OpenAI API credits)")
        
        # Check for API key
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        embedding_model = EmbeddingModel()
        vector_db = MetadataVectorDatabase(embedding_model=embedding_model)
        
        # Build with progress indication
        batch_size = 20
        total_batches = (len(self.chunks) + batch_size - 1) // batch_size
        
        for i in range(0, len(self.chunks), batch_size):
            batch_num = i // batch_size + 1
            batch_chunks = self.chunks[i:i + batch_size]
            batch_metadata = self.chunk_metadata[i:i + batch_size]
            
            print(f"   Processing batch {batch_num}/{total_batches}...")
            
            embeddings = embedding_model.get_embeddings(batch_chunks)
            
            for j, (chunk, embedding) in enumerate(zip(batch_chunks, embeddings)):
                import numpy as np
                vector_db.insert(chunk, np.array(embedding), batch_metadata[j])
        
        print(f"   ✓ Created {vector_db.get_size()} embeddings")
        return vector_db

    def save_database(self, vector_db: MetadataVectorDatabase) -> str:
        """Save the vector database to disk."""
        print(f"\n💾 Saving vector database to: {self.output_path}")
        
        vector_db.save(self.output_path)
        
        # Also save a metadata summary
        summary_path = self.output_path.replace(".json", "_summary.json")
        summary = {
            "created_at": datetime.now().isoformat(),
            "data_directory": self.data_directory,
            "num_documents": len(self.documents),
            "num_chunks": len(self.chunks),
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "sources": self.doc_sources,
            "topic_distribution": {},
            "difficulty_distribution": {}
        }
        
        for meta in self.chunk_metadata:
            topic = meta.get("topic", "unknown")
            difficulty = meta.get("difficulty", "unknown")
            summary["topic_distribution"][topic] = summary["topic_distribution"].get(topic, 0) + 1
            summary["difficulty_distribution"][difficulty] = summary["difficulty_distribution"].get(difficulty, 0) + 1
        
        with open(summary_path, "w") as f:
            json.dump(summary, f, indent=2)
        
        print(f"   ✓ Saved summary to: {summary_path}")
        return self.output_path

    def run(self) -> str:
        """Run the complete embedding pipeline."""
        print("=" * 60)
        print("🚀 EMBEDDING PIPELINE")
        print("=" * 60)
        
        self.load_documents()
        self.split_documents()
        vector_db = self.create_embeddings()
        output_path = self.save_database(vector_db)
        
        print("\n" + "=" * 60)
        print("✅ EMBEDDING COMPLETE")
        print("=" * 60)
        print(f"\nVector database saved to: {output_path}")
        print("You can now use the retrieval service (rag.py) to query this database.")
        
        return output_path


# ============ CLI Entry Point ============

def main():
    parser = argparse.ArgumentParser(
        description="Create embeddings and persist vector database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m api.embed
  python -m api.embed --data-dir ./data --output ./vectorstore/wellness_db.json
  python -m api.embed --chunk-size 300 --chunk-overlap 50
        """
    )
    
    # Determine default paths relative to this script
    script_dir = Path(__file__).parent
    default_data_dir = str(script_dir.parent / "data")
    default_output = str(script_dir.parent / "vectorstore" / "vector_db.json")
    
    parser.add_argument(
        "--data-dir",
        type=str,
        default=default_data_dir,
        help=f"Directory containing source documents (default: {default_data_dir})"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        default=default_output,
        help=f"Output path for vector database (default: {default_output})"
    )
    
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=500,
        help="Size of text chunks (default: 500)"
    )
    
    parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=100,
        help="Overlap between chunks (default: 100)"
    )
    
    args = parser.parse_args()
    
    # Validate data directory exists
    if not os.path.isdir(args.data_dir):
        print(f"Error: Data directory not found: {args.data_dir}")
        sys.exit(1)
    
    # Run the pipeline
    pipeline = EmbeddingPipeline(
        data_directory=args.data_dir,
        output_path=args.output,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap
    )
    
    try:
        pipeline.run()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
