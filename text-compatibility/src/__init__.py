"""
Text Compatibility - Source Module
==================================

Components:
- message_parser: Parse iMessage data from SQLite or JSON
- embeddings: Create vector embeddings using OpenAI
- vector_store: Store and query embeddings with ChromaDB
"""

from .message_parser import (
    Message,
    MessageWindow,
    IMessageParser,
    JSONParser,
    create_message_windows,
    create_sample_data
)

from .embeddings import (
    OpenAIEmbedder,
    EmbeddingResult,
    cosine_similarity
)

from .vector_store import (
    VectorStore,
    RAGPipeline,
    SearchResult
)

__all__ = [
    # Message Parser
    'Message',
    'MessageWindow', 
    'IMessageParser',
    'JSONParser',
    'create_message_windows',
    'create_sample_data',
    
    # Embeddings
    'OpenAIEmbedder',
    'EmbeddingResult',
    'cosine_similarity',
    
    # Vector Store
    'VectorStore',
    'RAGPipeline',
    'SearchResult',
]
