"""
Vector Store Module
===================
Handles storing and querying embeddings using ChromaDB.

ChromaDB is a local vector database that:
- Runs entirely on your machine (no API keys needed)
- Persists data to disk
- Supports fast similarity search
- Allows filtering by metadata

How Vector Search Works:
------------------------
1. You store vectors with their metadata
2. When querying, you provide a query vector
3. ChromaDB finds the most similar vectors using cosine similarity
4. You get back the most relevant results

This is how RAG (Retrieval-Augmented Generation) works:
- Store embeddings of all your messages
- When generating a response, embed the current conversation
- Find similar past messages
- Use those as context for the LLM
"""

import os
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
import json

import chromadb
from chromadb.config import Settings
from chromadb.errors import NotFoundError


@dataclass
class SearchResult:
    """A single search result from the vector store."""
    id: str
    text: str
    metadata: Dict[str, Any]
    distance: float  # Lower = more similar (ChromaDB uses L2 distance by default)
    similarity: float  # Converted to 0-1 scale (higher = more similar)


class VectorStore:
    """
    Vector database for storing and querying message embeddings.
    
    Architecture:
    -------------
    - Each USER gets their own collection
    - Each collection stores that user's message embeddings
    - Metadata includes: message_id, text, context, timestamp, etc.
    
    Why per-user collections?
    -------------------------
    When simulating User A's responses, we only want to search
    User A's past messages. Separate collections make this fast.
    
    Usage:
    ------
    >>> store = VectorStore("./my_database")
    >>> store.create_user_collection("alice")
    >>> store.add_messages("alice", messages, embeddings)
    >>> results = store.search("alice", query_embedding, top_k=5)
    """
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        """
        Initialize the vector store.
        
        Args:
            persist_directory: Where to save the database files.
                              Data persists across restarts.
        """
        self.persist_directory = persist_directory
        
        # Create ChromaDB client with persistence
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False  # Disable telemetry
            )
        )
        
        print(f"✓ Vector Store initialized")
        print(f"  Database location: {persist_directory}")
        print(f"  Existing collections: {self.list_collections()}")
    
    def list_collections(self) -> List[str]:
        """List all collection names in the database."""
        collections = self.client.list_collections()
        return [c.name for c in collections]
    
    def create_user_collection(
        self,
        user_id: str,
        overwrite: bool = False
    ) -> chromadb.Collection:
        """
        Create a collection for a user's messages.
        
        Args:
            user_id: Unique identifier for the user
            overwrite: If True, delete existing collection first
            
        Returns:
            The ChromaDB collection object
        """
        collection_name = f"user_{user_id}"
        
        if overwrite:
            try:
                self.client.delete_collection(collection_name)
                print(f"  Deleted existing collection: {collection_name}")
            except NotFoundError:
                # Collection doesn't exist, which is fine when overwriting
                pass
            except ValueError as e:
                # Older ChromaDB versions raise ValueError
                if "does not exist" in str(e).lower() or "not found" in str(e).lower():
                    pass  # Collection didn't exist, that's fine
                else:
                    raise  # Re-raise unexpected errors
        
        # Create or get the collection
        # Using cosine similarity (most common for text)
        collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}  # Use cosine similarity
        )
        
        print(f"✓ Collection ready: {collection_name}")
        return collection
    
    def get_user_collection(self, user_id: str) -> chromadb.Collection:
        """
        Get an existing user collection.
        
        Args:
            user_id: The user's identifier
            
        Returns:
            The ChromaDB collection
            
        Raises:
            ValueError: If collection doesn't exist
        """
        collection_name = f"user_{user_id}"
        try:
            return self.client.get_collection(collection_name)
        except ValueError:
            raise ValueError(
                f"No collection found for user '{user_id}'. "
                f"Create one first with create_user_collection()"
            )
    
    def add_messages(
        self,
        user_id: str,
        message_windows: List[Dict],
        embeddings: List[List[float]]
    ) -> int:
        """
        Add message embeddings to a user's collection.
        
        Args:
            user_id: The user whose messages these are
            message_windows: List of message window dicts with keys:
                - message_id: Unique ID
                - message_text: The actual message
                - context: Surrounding conversation
                - timestamp: When it was sent
            embeddings: Corresponding embedding vectors
            
        Returns:
            Number of messages added
        """
        if len(message_windows) != len(embeddings):
            raise ValueError(
                f"Mismatch: {len(message_windows)} messages but {len(embeddings)} embeddings"
            )
        
        collection = self.get_user_collection(user_id)
        
        # Prepare data for ChromaDB
        ids = []
        documents = []
        metadatas = []
        
        for i, window in enumerate(message_windows):
            ids.append(f"{user_id}_{window['message_id']}")
            documents.append(window['context'])  # Store full context as document
            metadatas.append({
                'message_id': window['message_id'],
                'message_text': window['message_text'],
                'timestamp': window.get('timestamp', ''),
                'sender_id': window.get('sender_id', user_id),
                'user_id': user_id
            })
        
        # Add to collection
        collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )
        
        print(f"✓ Added {len(ids)} messages to collection 'user_{user_id}'")
        return len(ids)
    
    def search(
        self,
        user_id: str,
        query_embedding: List[float],
        top_k: int = 10,
        filter_dict: Optional[Dict] = None
    ) -> List[SearchResult]:
        """
        Search for similar messages in a user's collection.
        
        This is the core of RAG - finding relevant past messages
        to use as context when generating a response.
        
        Args:
            user_id: Whose messages to search
            query_embedding: The embedding of the current conversation
            top_k: Number of results to return
            filter_dict: Optional metadata filters
            
        Returns:
            List of SearchResult objects, sorted by similarity
        """
        collection = self.get_user_collection(user_id)
        
        # Query ChromaDB
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=filter_dict,
            include=['documents', 'metadatas', 'distances']
        )
        
        # Convert to SearchResult objects
        search_results = []
        
        # Results come back as lists of lists (to support multiple queries)
        if results['ids'] and results['ids'][0]:
            for i in range(len(results['ids'][0])):
                distance = results['distances'][0][i]
                
                # Convert distance to similarity (0-1 scale)
                # For cosine distance: similarity = 1 - distance
                # ChromaDB returns squared L2 for cosine, so we adjust
                similarity = max(0, 1 - distance)
                
                search_results.append(SearchResult(
                    id=results['ids'][0][i],
                    text=results['documents'][0][i],
                    metadata=results['metadatas'][0][i],
                    distance=distance,
                    similarity=similarity
                ))
        
        return search_results
    
    def get_collection_stats(self, user_id: str) -> Dict:
        """
        Get statistics about a user's collection.
        
        Args:
            user_id: The user's identifier
            
        Returns:
            Dict with collection statistics
        """
        collection = self.get_user_collection(user_id)
        
        return {
            'user_id': user_id,
            'collection_name': collection.name,
            'total_messages': collection.count(),
            'metadata': collection.metadata
        }
    
    def delete_user_collection(self, user_id: str):
        """Delete a user's entire collection."""
        collection_name = f"user_{user_id}"
        try:
            self.client.delete_collection(collection_name)
            print(f"✓ Deleted collection: {collection_name}")
        except NotFoundError:
            print(f"Collection '{collection_name}' not found")
        except ValueError as e:
            if "does not exist" in str(e).lower() or "not found" in str(e).lower():
                print(f"Collection '{collection_name}' not found")
            else:
                raise
    
    def clear_all(self):
        """Delete ALL collections. Use with caution!"""
        for name in self.list_collections():
            self.client.delete_collection(name)
        print("✓ All collections deleted")


class RAGPipeline:
    """
    Complete RAG pipeline combining embeddings and vector search.
    
    This class ties together:
    1. Message parsing
    2. Embedding creation
    3. Vector storage
    4. Retrieval
    
    Usage:
    ------
    >>> from embeddings import OpenAIEmbedder
    >>> 
    >>> embedder = OpenAIEmbedder()
    >>> store = VectorStore("./my_db")
    >>> pipeline = RAGPipeline(embedder, store)
    >>> 
    >>> # Index a user's messages
    >>> pipeline.index_user_messages("alice", message_windows)
    >>> 
    >>> # Retrieve relevant context
    >>> context = pipeline.retrieve_context("alice", "want to get dinner?")
    """
    
    def __init__(self, embedder, vector_store: VectorStore):
        """
        Initialize the RAG pipeline.
        
        Args:
            embedder: An embedder instance (OpenAIEmbedder)
            vector_store: A VectorStore instance
        """
        self.embedder = embedder
        self.store = vector_store
    
    def index_user_messages(
        self,
        user_id: str,
        message_windows: List[Dict],
        overwrite: bool = False
    ) -> int:
        """
        Index all of a user's messages for retrieval.
        
        This processes messages and stores them in the vector database,
        making them searchable for future conversations.
        
        Args:
            user_id: Unique identifier for the user
            message_windows: List of message window dicts
            overwrite: Whether to replace existing data
            
        Returns:
            Number of messages indexed
        """
        print(f"\n📚 Indexing messages for user: {user_id}")
        
        # Create collection
        self.store.create_user_collection(user_id, overwrite=overwrite)
        
        # Extract contexts to embed
        contexts = [w['context'] for w in message_windows]
        
        # Create embeddings
        print(f"  Creating embeddings for {len(contexts)} message windows...")
        embedding_results = self.embedder.embed_batch(contexts)
        embeddings = [r.embedding for r in embedding_results]
        
        # Store in vector database
        count = self.store.add_messages(user_id, message_windows, embeddings)
        
        print(f"✓ Indexed {count} messages for {user_id}")
        return count
    
    def retrieve_context(
        self,
        user_id: str,
        current_conversation: str,
        top_k: int = 8
    ) -> List[Dict]:
        """
        Retrieve relevant past messages for context.
        
        Given the current conversation, find similar past situations
        from this user's history to use as examples.
        
        Args:
            user_id: Whose style we're trying to match
            current_conversation: The recent conversation text
            top_k: Number of examples to retrieve
            
        Returns:
            List of relevant past message contexts
        """
        # Embed the current conversation
        query_embedding = self.embedder.embed_for_query(current_conversation)
        
        # Search for similar past contexts
        results = self.store.search(user_id, query_embedding, top_k=top_k)
        
        # Format results
        contexts = []
        for result in results:
            contexts.append({
                'context': result.text,
                'response': result.metadata.get('message_text', ''),
                'similarity': result.similarity,
                'timestamp': result.metadata.get('timestamp', '')
            })
        
        return contexts
    
    def format_context_for_prompt(self, contexts: List[Dict]) -> str:
        """
        Format retrieved contexts for use in an LLM prompt.
        
        Args:
            contexts: List of context dicts from retrieve_context()
            
        Returns:
            Formatted string ready to include in a prompt
        """
        formatted_parts = []
        
        for i, ctx in enumerate(contexts, 1):
            formatted_parts.append(
                f"Example {i} (similarity: {ctx['similarity']:.2f}):\n"
                f"Conversation:\n{ctx['context']}\n"
                f"---"
            )
        
        return "\n\n".join(formatted_parts)


def demonstrate_vector_store():
    """
    Demonstrate the vector store functionality.
    
    This creates a sample database, adds messages, and shows
    how similarity search works.
    """
    import tempfile
    import os as os_module
    
    print("=" * 60)
    print("VECTOR STORE DEMONSTRATION")
    print("=" * 60)
    
    # Check for API key
    if not os_module.environ.get('OPENAI_API_KEY'):
        print("\n⚠️  No OPENAI_API_KEY found in environment!")
        print("Set it with: export OPENAI_API_KEY='your-key'")
        print("\nSkipping demonstration that requires embeddings.")
        
        # Show basic ChromaDB functionality without embeddings
        print("\n--- Basic ChromaDB Demo (no embeddings needed) ---\n")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            store = VectorStore(tmpdir)
            store.create_user_collection("demo_user")
            
            # Add some fake embeddings (just for demo)
            fake_windows = [
                {'message_id': '1', 'message_text': 'hello', 'context': 'greeting'},
                {'message_id': '2', 'message_text': 'bye', 'context': 'farewell'},
            ]
            fake_embeddings = [[0.1] * 1536, [0.2] * 1536]  # Dummy 1536-dim vectors
            
            store.add_messages("demo_user", fake_windows, fake_embeddings)
            
            stats = store.get_collection_stats("demo_user")
            print(f"Collection stats: {stats}")
        
        return
    
    # Full demo with real embeddings
    from embeddings import OpenAIEmbedder
    from message_parser import JSONParser, create_message_windows, create_sample_data
    
    with tempfile.TemporaryDirectory() as tmpdir:
        print(f"\n📁 Using temporary database: {tmpdir}\n")
        
        # Initialize components
        embedder = OpenAIEmbedder()
        store = VectorStore(tmpdir)
        pipeline = RAGPipeline(embedder, store)
        
        # Load sample data
        print("\n📝 Loading sample conversation...")
        sample_data = create_sample_data()
        parser = JSONParser(my_user_id="alice")
        messages = parser.parse_data(sample_data)
        
        # Create windows and filter to Alice's messages only
        all_windows = create_message_windows(messages, window_size=2)
        alice_windows = [w.to_dict() for w in all_windows if w.is_from_me]
        
        print(f"  Found {len(alice_windows)} messages from Alice")
        
        # Index Alice's messages
        pipeline.index_user_messages("alice", alice_windows, overwrite=True)
        
        # Now test retrieval with different queries
        print("\n" + "=" * 60)
        print("TESTING RETRIEVAL")
        print("=" * 60)
        
        test_queries = [
            "want to grab food tonight?",
            "did you finish your homework?",
            "are you coming to the event?",
        ]
        
        for query in test_queries:
            print(f"\n🔍 Query: \"{query}\"")
            print("-" * 40)
            
            contexts = pipeline.retrieve_context("alice", query, top_k=3)
            
            for ctx in contexts:
                print(f"\n  Similarity: {ctx['similarity']:.3f}")
                print(f"  Her response: \"{ctx['response']}\"")
                print(f"  Context: {ctx['context'][:100]}...")
        
        print("\n" + "=" * 60)
        print("Demo complete! The database was temporary and has been deleted.")
        print("=" * 60)


if __name__ == "__main__":
    demonstrate_vector_store()
