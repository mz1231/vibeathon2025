"""
Embeddings Module
=================
Handles creating vector embeddings using OpenAI's API.

SETUP:
------
Set your API key as an environment variable:
    export OPENAI_API_KEY="your-api-key-here"

This module reads from the environment, so your key is never in the code.
"""

import os
from typing import List, Optional
from dataclasses import dataclass
import time

from openai import OpenAI
from tqdm import tqdm


@dataclass
class EmbeddingResult:
    """Result of an embedding operation."""
    text: str
    embedding: List[float]
    model: str
    dimensions: int


class OpenAIEmbedder:
    """
    Creates embeddings using OpenAI's API.
    
    What is an embedding?
    ---------------------
    An embedding converts text into a list of numbers (a vector) that
    captures the MEANING of that text. Similar texts have similar vectors.
    
    Example:
        "I love pizza" → [0.23, -0.45, 0.12, ..., 0.67]  (1536 numbers)
        "Pizza is great" → [0.25, -0.42, 0.15, ..., 0.64]  (similar!)
        "Stock prices fell" → [0.89, 0.12, -0.77, ..., -0.34]  (very different)
    
    Why OpenAI's embeddings?
    ------------------------
    - High quality semantic understanding
    - text-embedding-3-small is fast and cheap ($0.02 per 1M tokens)
    - 1536 dimensions capture nuanced meaning
    
    Usage:
    ------
    >>> embedder = OpenAIEmbedder()
    >>> result = embedder.embed("Hello world")
    >>> print(len(result.embedding))  # 1536
    """
    
    # Available models and their dimensions
    MODELS = {
        'text-embedding-3-small': 1536,
        'text-embedding-3-large': 3072,
        'text-embedding-ada-002': 1536,  # Legacy, but still works
    }
    
    def __init__(
        self,
        model: str = 'text-embedding-3-small',
        api_key: Optional[str] = None
    ):
        """
        Initialize the embedder.
        
        Args:
            model: OpenAI embedding model to use
            api_key: OpenAI API key. If None, reads from OPENAI_API_KEY env var
            
        Raises:
            ValueError: If no API key is found
        """
        # Get API key from environment if not provided
        self.api_key = api_key or os.environ.get('OPENAI_API_KEY')
        
        if not self.api_key:
            raise ValueError(
                "No OpenAI API key found!\n"
                "Set it as an environment variable:\n"
                "  export OPENAI_API_KEY='your-key-here'\n"
                "Or pass it directly to OpenAIEmbedder(api_key='...')"
            )
        
        if model not in self.MODELS:
            raise ValueError(f"Unknown model: {model}. Choose from: {list(self.MODELS.keys())}")
        
        self.model = model
        self.dimensions = self.MODELS[model]
        
        # Initialize the OpenAI client
        self.client = OpenAI(api_key=self.api_key)
        
        print(f"✓ OpenAI Embedder initialized")
        print(f"  Model: {self.model}")
        print(f"  Dimensions: {self.dimensions}")
    
    def embed(self, text: str) -> EmbeddingResult:
        """
        Create an embedding for a single text.
        
        Args:
            text: The text to embed
            
        Returns:
            EmbeddingResult with the embedding vector
        """
        # Clean and validate text
        text = text.strip()
        if not text:
            raise ValueError("Cannot embed empty text")
        
        # Call OpenAI API
        response = self.client.embeddings.create(
            model=self.model,
            input=text
        )
        
        embedding = response.data[0].embedding
        
        return EmbeddingResult(
            text=text,
            embedding=embedding,
            model=self.model,
            dimensions=len(embedding)
        )
    
    def embed_batch(
        self,
        texts: List[str],
        batch_size: int = 100,
        show_progress: bool = True
    ) -> List[EmbeddingResult]:
        """
        Create embeddings for multiple texts efficiently.
        
        OpenAI's API can process multiple texts in one request,
        which is faster and more cost-effective than one-by-one.
        
        Args:
            texts: List of texts to embed
            batch_size: Number of texts per API call (max 2048)
            show_progress: Whether to show a progress bar
            
        Returns:
            List of EmbeddingResult objects
        """
        results = []
        
        # Filter out empty texts and track their indices
        valid_texts = []
        valid_indices = []
        for i, text in enumerate(texts):
            cleaned = text.strip() if text else ""
            if cleaned:
                valid_texts.append(cleaned)
                valid_indices.append(i)
        
        if not valid_texts:
            return results
        
        # Process in batches
        iterator = range(0, len(valid_texts), batch_size)
        if show_progress:
            iterator = tqdm(iterator, desc="Creating embeddings", unit="batch")
        
        for i in iterator:
            batch = valid_texts[i:i + batch_size]
            
            # Call OpenAI API with batch
            response = self.client.embeddings.create(
                model=self.model,
                input=batch
            )
            
            # Extract embeddings (they come back in order)
            for j, embedding_data in enumerate(response.data):
                results.append(EmbeddingResult(
                    text=batch[j],
                    embedding=embedding_data.embedding,
                    model=self.model,
                    dimensions=len(embedding_data.embedding)
                ))
            
            # Small delay to avoid rate limits
            if i + batch_size < len(valid_texts):
                time.sleep(0.1)
        
        return results
    
    def embed_for_query(self, query: str) -> List[float]:
        """
        Create an embedding specifically for searching.
        
        This is a convenience method that returns just the vector,
        ready to use with ChromaDB's query method.
        
        Args:
            query: The search query text
            
        Returns:
            List of floats (the embedding vector)
        """
        result = self.embed(query)
        return result.embedding


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Calculate cosine similarity between two vectors.
    
    Cosine similarity measures how similar two vectors are based on
    their direction, ignoring magnitude. Returns a value from -1 to 1:
        - 1.0 = identical direction (very similar)
        - 0.0 = perpendicular (unrelated)
        - -1.0 = opposite direction (opposite meaning)
    
    For text embeddings, values typically range from 0.3 to 0.95.
    
    Args:
        vec1: First embedding vector
        vec2: Second embedding vector
        
    Returns:
        Similarity score from -1 to 1
    """
    import math
    
    # Dot product
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    
    # Magnitudes
    magnitude1 = math.sqrt(sum(a * a for a in vec1))
    magnitude2 = math.sqrt(sum(b * b for b in vec2))
    
    # Avoid division by zero
    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0
    
    return dot_product / (magnitude1 * magnitude2)


def demonstrate_embeddings():
    """
    Interactive demonstration of how embeddings work.
    
    Run this to see embeddings in action and understand
    how similar texts have similar vectors.
    """
    print("=" * 60)
    print("EMBEDDING DEMONSTRATION")
    print("=" * 60)
    
    # Check for API key
    if not os.environ.get('OPENAI_API_KEY'):
        print("\n⚠️  No OPENAI_API_KEY found in environment!")
        print("Set it with: export OPENAI_API_KEY='your-key'")
        return
    
    embedder = OpenAIEmbedder()
    
    # Test sentences - some similar, some different
    test_sentences = [
        "I love eating pizza",
        "Pizza is my favorite food",
        "I enjoy Italian cuisine",
        "The stock market crashed today",
        "Bitcoin prices are falling",
        "want to grab dinner tonight?",
        "let's get food later",
        "are you free to eat?",
    ]
    
    print("\n📝 Creating embeddings for test sentences...")
    results = embedder.embed_batch(test_sentences, show_progress=False)
    
    print("\n📊 Similarity Matrix:")
    print("-" * 60)
    
    # Compare first sentence to all others
    base_sentence = test_sentences[0]
    base_embedding = results[0].embedding
    
    print(f"\nComparing everything to: \"{base_sentence}\"\n")
    
    similarities = []
    for i, result in enumerate(results):
        sim = cosine_similarity(base_embedding, result.embedding)
        similarities.append((test_sentences[i], sim))
    
    # Sort by similarity
    similarities.sort(key=lambda x: x[1], reverse=True)
    
    for sentence, sim in similarities:
        # Visual bar
        bar_length = int(sim * 30)
        bar = "█" * bar_length + "░" * (30 - bar_length)
        print(f"  {sim:.3f} [{bar}] \"{sentence}\"")
    
    print("\n" + "=" * 60)
    print("Notice how semantically similar sentences have higher scores!")
    print("=" * 60)


# Run demonstration when executed directly
if __name__ == "__main__":
    demonstrate_embeddings()
