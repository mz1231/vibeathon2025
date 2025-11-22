"""
Vector-Based Conversation Simulator
====================================
Two LLMs chat with each other using real embeddings and vector search
to retrieve relevant message examples from iMessage history.
"""

import os
import json
import numpy as np
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from collections import Counter
import re


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class UserProfile:
    """Stores analyzed texting style characteristics for a user."""
    user_id: str
    avg_length: float
    uses_emojis: bool
    emoji_frequency: float
    capitalization: str  # 'lowercase', 'sentence_case', 'mixed'
    common_phrases: List[str]
    punctuation_style: str
    vocabulary_richness: float


# ============================================================================
# IMESSAGE DATA PARSER
# ============================================================================

class iMessageParser:
    """
    Parses iMessage JSON data into context/response pairs suitable for RAG.
    """

    @staticmethod
    def load_messages(file_path: str) -> List[Dict]:
        """Load messages from JSON file."""
        with open(file_path, 'r') as f:
            data = json.load(f)

        # Handle both array and object with 'messages' key
        if isinstance(data, dict) and 'messages' in data:
            return data['messages']
        elif isinstance(data, list):
            return data
        else:
            raise ValueError("Unexpected JSON format")

    @staticmethod
    def create_context_response_pairs(
        messages: List[Dict],
        window_size: int = 3,
        min_text_length: int = 2
    ) -> List[Dict]:
        """
        Convert iMessage format to context/response pairs.

        Groups messages by chat_id and creates pairs where:
        - context: previous messages in the conversation
        - response: the user's message

        Args:
            messages: Raw iMessage data
            window_size: Number of previous messages to include as context
            min_text_length: Minimum text length to include

        Returns:
            List of {context, response, timestamp, chat_id} dicts
        """
        # Group messages by chat_id
        chats: Dict[int, List[Dict]] = {}
        for msg in messages:
            chat_id = msg.get('chat_id', 0)
            if chat_id not in chats:
                chats[chat_id] = []
            chats[chat_id].append(msg)

        # Sort each chat by timestamp
        for chat_id in chats:
            chats[chat_id].sort(key=lambda x: x.get('timestamp', ''))

        pairs = []

        for chat_id, chat_messages in chats.items():
            for i, msg in enumerate(chat_messages):
                text = msg.get('text', '')

                # Skip empty or very short messages
                if not text or len(text.strip()) < min_text_length:
                    continue

                # Skip messages that are just attachments
                if msg.get('has_attachments') and not text:
                    continue

                # Build context from previous messages
                start_idx = max(0, i - window_size)
                context_messages = chat_messages[start_idx:i]

                if context_messages:
                    # Format context as "Them: message" for previous messages
                    context_parts = []
                    for ctx_msg in context_messages:
                        ctx_text = ctx_msg.get('text', '')
                        if ctx_text:
                            context_parts.append(f"Them: {ctx_text}")

                    context = "\n".join(context_parts) if context_parts else "Them: [conversation start]"
                else:
                    context = "Them: [conversation start]"

                pairs.append({
                    'context': context,
                    'response': text,
                    'timestamp': msg.get('timestamp', ''),
                    'chat_id': chat_id
                })

        return pairs


# ============================================================================
# EMBEDDING SYSTEM (Real OpenAI Embeddings)
# ============================================================================

class EmbeddingService:
    """
    Handles creation of embeddings using OpenAI's API.
    Falls back to mock embeddings if API is not available.
    """

    def __init__(self):
        self.client = None
        self.model = "text-embedding-3-small"
        self.dimension = 1536  # text-embedding-3-small dimension
        self._init_client()

    def _init_client(self):
        """Initialize OpenAI client."""
        try:
            from openai import OpenAI
            api_key = os.environ.get("OPENAI_API_KEY")
            if api_key:
                self.client = OpenAI(api_key=api_key)
                print("✓ OpenAI embedding service initialized")
            else:
                print("⚠ OPENAI_API_KEY not set - using mock embeddings")
        except ImportError:
            print("⚠ openai not installed - using mock embeddings")

    def create_embedding(self, text: str) -> np.ndarray:
        """Create embedding for a single text."""
        if self.client:
            try:
                response = self.client.embeddings.create(
                    model=self.model,
                    input=text
                )
                return np.array(response.data[0].embedding)
            except Exception as e:
                print(f"Embedding error: {e}")
                return self._mock_embedding(text)
        else:
            return self._mock_embedding(text)

    def create_embeddings_batch(self, texts: List[str], batch_size: int = 100) -> List[np.ndarray]:
        """Create embeddings for multiple texts in batches."""
        embeddings = []

        if self.client:
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                try:
                    response = self.client.embeddings.create(
                        model=self.model,
                        input=batch
                    )
                    for item in response.data:
                        embeddings.append(np.array(item.embedding))

                    if i % 500 == 0 and i > 0:
                        print(f"  Processed {i}/{len(texts)} embeddings...")

                except Exception as e:
                    print(f"Batch embedding error: {e}")
                    # Fall back to mock for this batch
                    for text in batch:
                        embeddings.append(self._mock_embedding(text))
        else:
            embeddings = [self._mock_embedding(t) for t in texts]

        return embeddings

    def _mock_embedding(self, text: str) -> np.ndarray:
        """Create mock embedding based on text characteristics."""
        features = [
            len(text) / 100,
            text.count('!') / max(len(text), 1) * 10,
            text.count('?') / max(len(text), 1) * 10,
            1.0 if any(c in text for c in '😀😂🙂❤️👍🎉😭🔥💀') else 0.0,
            sum(1 for c in text if c.isupper()) / max(len(text), 1),
            len(text.split()) / 20,
            text.count('lol') + text.count('haha') + text.count('lmao'),
            1.0 if text.endswith('?') else 0.0,
        ]

        embedding = np.zeros(self.dimension)
        embedding[:len(features)] = features
        embedding += np.random.randn(self.dimension) * 0.01

        return embedding


# ============================================================================
# VECTOR DATABASE
# ============================================================================

class VectorDB:
    """
    Vector database for storing and retrieving message embeddings.
    Uses cosine similarity for semantic search.
    """

    def __init__(self):
        self.vectors: Dict[str, Dict] = {}
        self.embedding_matrix: Optional[np.ndarray] = None
        self.id_list: List[str] = []

    def upsert(self, id: str, embedding: np.ndarray, metadata: Dict):
        """Store a vector with its metadata."""
        self.vectors[id] = {
            'embedding': embedding,
            'metadata': metadata
        }
        # Invalidate cache
        self.embedding_matrix = None

    def build_index(self):
        """Build matrix index for faster search."""
        if self.vectors:
            self.id_list = list(self.vectors.keys())
            self.embedding_matrix = np.array([
                self.vectors[id]['embedding'] for id in self.id_list
            ])
            # Normalize for cosine similarity
            norms = np.linalg.norm(self.embedding_matrix, axis=1, keepdims=True)
            self.embedding_matrix = self.embedding_matrix / (norms + 1e-8)

    def query(
        self,
        vector: np.ndarray,
        top_k: int = 10,
        filter: Optional[Dict] = None
    ) -> Dict:
        """
        Find the most similar vectors using cosine similarity.

        Args:
            vector: Query embedding
            top_k: Number of results to return
            filter: Metadata filters (e.g., {"user_id": {"$eq": "user_a"}})

        Returns:
            Dictionary with 'matches' containing scored results
        """
        results = []

        # Normalize query vector
        query_norm = vector / (np.linalg.norm(vector) + 1e-8)

        # Use matrix multiplication if index is built
        if self.embedding_matrix is not None and filter is None:
            similarities = self.embedding_matrix @ query_norm
            top_indices = np.argsort(similarities)[::-1][:top_k]

            for idx in top_indices:
                id = self.id_list[idx]
                results.append({
                    'id': id,
                    'score': float(similarities[idx]),
                    'metadata': self.vectors[id]['metadata']
                })
        else:
            # Fall back to linear search with filtering
            for id, data in self.vectors.items():
                # Apply filters
                if filter:
                    match = True
                    for key, condition in filter.items():
                        if '$eq' in condition:
                            if data['metadata'].get(key) != condition['$eq']:
                                match = False
                                break
                    if not match:
                        continue

                # Calculate cosine similarity
                stored_vec = data['embedding']
                stored_norm = stored_vec / (np.linalg.norm(stored_vec) + 1e-8)
                similarity = float(np.dot(query_norm, stored_norm))

                results.append({
                    'id': id,
                    'score': similarity,
                    'metadata': data['metadata']
                })

            # Sort by similarity
            results.sort(key=lambda x: x['score'], reverse=True)
            results = results[:top_k]

        return {'matches': results}

    def get_stats(self) -> Dict:
        """Get database statistics."""
        return {
            'total_vectors': len(self.vectors),
            'has_index': self.embedding_matrix is not None
        }


# ============================================================================
# USER STYLE ANALYSIS
# ============================================================================

def analyze_user_style(messages: List[Dict]) -> UserProfile:
    """
    Analyze a user's texting style from their message history.
    """
    texts = [msg['response'] for msg in messages]

    if not texts:
        return UserProfile(
            user_id="",
            avg_length=20,
            uses_emojis=False,
            emoji_frequency=0,
            capitalization='mixed',
            common_phrases=[],
            punctuation_style='minimal',
            vocabulary_richness=0.5
        )

    # Average message length
    avg_length = sum(len(t) for t in texts) / len(texts)

    # Emoji detection
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"
        "\U0001F300-\U0001F5FF"
        "\U0001F680-\U0001F6FF"
        "\U0001F1E0-\U0001F1FF"
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "]+",
        flags=re.UNICODE
    )

    emoji_count = sum(len(emoji_pattern.findall(t)) for t in texts)
    uses_emojis = emoji_count > len(texts) * 0.1
    emoji_frequency = emoji_count / len(texts)

    # Capitalization style
    first_char_caps = sum(1 for t in texts if t and t[0].isupper())
    caps_ratio = first_char_caps / len(texts)

    if caps_ratio > 0.8:
        capitalization = 'sentence_case'
    elif caps_ratio < 0.2:
        capitalization = 'lowercase'
    else:
        capitalization = 'mixed'

    # Common phrases (bigrams)
    bigrams = []
    for text in texts:
        words = text.lower().split()
        for i in range(len(words) - 1):
            bigrams.append(f"{words[i]} {words[i+1]}")

    phrase_freq = Counter(bigrams)
    common_phrases = [phrase for phrase, count in phrase_freq.most_common(5) if count > 1]

    # Punctuation style
    exclamation_count = sum(t.count('!') for t in texts)
    period_count = sum(t.count('.') for t in texts)

    if exclamation_count > period_count:
        punctuation_style = 'exclamatory'
    elif period_count > len(texts) * 0.5:
        punctuation_style = 'formal'
    else:
        punctuation_style = 'minimal'

    # Vocabulary richness
    all_words = ' '.join(texts).lower().split()
    unique_words = len(set(all_words))
    total_words = len(all_words)
    vocabulary_richness = unique_words / total_words if total_words > 0 else 0

    return UserProfile(
        user_id="",
        avg_length=round(avg_length, 1),
        uses_emojis=uses_emojis,
        emoji_frequency=round(emoji_frequency, 2),
        capitalization=capitalization,
        common_phrases=common_phrases,
        punctuation_style=punctuation_style,
        vocabulary_richness=round(vocabulary_richness, 2)
    )


# ============================================================================
# MAIN SIMULATOR
# ============================================================================

class VectorConversationSimulator:
    """
    Simulates conversations between two users using real embeddings
    and vector search for RAG.
    """

    def __init__(self, llm_provider: str = "openai"):
        self.vector_db = VectorDB()
        self.embedding_service = EmbeddingService()
        self.user_profiles: Dict[str, UserProfile] = {}
        self.messages_data: Dict[str, List[Dict]] = {}
        self.llm_provider = llm_provider

        # Initialize LLM client
        self.client = None
        self._init_llm_client()

    def _init_llm_client(self):
        """Initialize the LLM client based on provider."""
        if self.llm_provider == "openai":
            try:
                from openai import OpenAI
                api_key = os.environ.get("OPENAI_API_KEY")
                if api_key:
                    self.client = OpenAI(api_key=api_key)
                    self.chat_model = "gpt-4o-mini"
                    print("✓ OpenAI LLM client initialized")
                else:
                    print("⚠ OPENAI_API_KEY not set for LLM")
            except ImportError:
                print("⚠ openai not installed for LLM")

        elif self.llm_provider == "anthropic":
            try:
                import anthropic
                api_key = os.environ.get("ANTHROPIC_API_KEY")
                if api_key:
                    self.client = anthropic.Anthropic(api_key=api_key)
                    self.chat_model = "claude-3-5-sonnet-20241022"
                    print("✓ Anthropic LLM client initialized")
                else:
                    print("⚠ ANTHROPIC_API_KEY not set for LLM")
            except ImportError:
                print("⚠ anthropic not installed for LLM")

    def setup_user_from_file(self, user_id: str, file_path: str):
        """
        Initialize a user from their iMessage JSON file.

        Args:
            user_id: Unique user identifier
            file_path: Path to the iMessage JSON file
        """
        print(f"\nSetting up user '{user_id}' from {file_path}...")

        # Load and parse messages
        raw_messages = iMessageParser.load_messages(file_path)
        print(f"  Loaded {len(raw_messages)} raw messages")

        # Convert to context/response pairs
        pairs = iMessageParser.create_context_response_pairs(raw_messages)
        print(f"  Created {len(pairs)} context/response pairs")

        # Setup user with pairs
        self.setup_user(user_id, pairs)

    def setup_user(self, user_id: str, messages: List[Dict]):
        """
        Initialize a user with their message history.

        Args:
            user_id: Unique user identifier
            messages: List of message records with 'context' and 'response' keys
        """
        self.messages_data[user_id] = messages

        # Analyze user style
        profile = analyze_user_style(messages)
        profile.user_id = user_id
        self.user_profiles[user_id] = profile

        # Create embeddings for all messages
        print(f"  Creating embeddings for {len(messages)} messages...")

        # Combine context and response for richer embeddings
        texts = [f"{m['context']}\nResponse: {m['response']}" for m in messages]
        embeddings = self.embedding_service.create_embeddings_batch(texts)

        # Store in vector DB
        for i, (msg, embedding) in enumerate(zip(messages, embeddings)):
            self.vector_db.upsert(
                id=f"{user_id}_{i}",
                embedding=embedding,
                metadata={
                    'user_id': user_id,
                    'context': msg['context'],
                    'response': msg['response'],
                    'timestamp': msg.get('timestamp', '')
                }
            )

        print(f"\n✓ User '{user_id}' initialized:")
        print(f"  - {len(messages)} messages indexed")
        print(f"  - Avg length: {profile.avg_length} chars")
        print(f"  - Style: {profile.capitalization}, {profile.punctuation_style}")
        print(f"  - Uses emojis: {'Yes' if profile.uses_emojis else 'Rarely/No'}")
        print()

    def _build_system_prompt(self, user_id: str) -> str:
        """Build a system prompt for the LLM to adopt the user's persona."""
        profile = self.user_profiles[user_id]

        return f"""You are simulating how a specific person texts. You must respond EXACTLY as they would - matching their texting style perfectly.

CRITICAL STYLE RULES:
- Average message length: {profile.avg_length} characters (stay close to this!)
- Capitalization: {profile.capitalization}
- Punctuation style: {profile.punctuation_style}
- Uses emojis: {'Yes' if profile.uses_emojis else 'Rarely/No'}
- Common phrases they use: {', '.join(profile.common_phrases) if profile.common_phrases else 'N/A'}

IMPORTANT:
- Match their exact tone, energy, and vocabulary
- Keep responses natural and conversational
- Don't be overly formal or verbose if their style is casual
- Don't be too brief if their style is more detailed
- Respond with ONLY the message text - no quotes, no "Response:", nothing extra"""

    def _build_user_prompt(
        self,
        user_id: str,
        conversation_history: List[Dict],
        retrieved_examples: List[Dict]
    ) -> str:
        """Build the user prompt with retrieved examples and conversation."""

        # Format retrieved examples
        examples_text = "EXAMPLES OF HOW THIS PERSON RESPONDS:\n\n"
        for i, ex in enumerate(retrieved_examples[:6], 1):
            examples_text += f"Context: {ex['context']}\n"
            examples_text += f"Their response: {ex['response']}\n\n"

        # Format current conversation
        conv_text = "CURRENT CONVERSATION:\n"
        for msg in conversation_history:
            sender_label = "You" if msg['sender'] == user_id else "Them"
            conv_text += f"{sender_label}: {msg['text']}\n"

        return f"""{examples_text}
{conv_text}
Now respond as this person would. Remember to match their style exactly."""

    def retrieve_similar_messages(
        self,
        user_id: str,
        context: str,
        top_k: int = 8
    ) -> List[Dict]:
        """
        Find past messages similar to the current context.

        Args:
            user_id: Whose messages to search
            context: Current conversation context
            top_k: How many examples to retrieve

        Returns:
            List of retrieved examples with context, response, and score
        """
        # Create embedding for query
        query_embedding = self.embedding_service.create_embedding(context)

        # Search vector database
        results = self.vector_db.query(
            vector=query_embedding,
            top_k=top_k,
            filter={"user_id": {"$eq": user_id}}
        )

        # Extract results
        retrieved = []
        for match in results['matches']:
            retrieved.append({
                'context': match['metadata']['context'],
                'response': match['metadata']['response'],
                'similarity': match['score']
            })

        return retrieved

    def generate_response(
        self,
        user_id: str,
        conversation_history: List[Dict],
        temperature: float = 0.9
    ) -> str:
        """
        Generate a response for the specified user using LLM.
        """
        # Format recent context for retrieval
        recent = conversation_history[-4:] if len(conversation_history) > 4 else conversation_history
        context_for_retrieval = self._format_conversation(recent)

        # Retrieve similar examples
        retrieved = self.retrieve_similar_messages(
            user_id,
            context_for_retrieval,
            top_k=8
        )

        # Build prompts
        system_prompt = self._build_system_prompt(user_id)
        user_prompt = self._build_user_prompt(user_id, conversation_history, retrieved)

        # Generate with LLM
        if self.client and self.llm_provider == "openai":
            response = self.client.chat.completions.create(
                model=self.chat_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=100
            )
            return response.choices[0].message.content.strip()

        elif self.client and self.llm_provider == "anthropic":
            response = self.client.messages.create(
                model=self.chat_model,
                max_tokens=100,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )
            return response.content[0].text.strip()

        else:
            # Fallback mock response
            return self._mock_response(user_id, retrieved)

    def _format_conversation(self, messages: List[Dict]) -> str:
        """Format a list of messages into a conversation string."""
        lines = []
        for msg in messages:
            sender = msg.get('sender', 'Unknown')
            text = msg.get('text', '')
            lines.append(f"{sender}: {text}")
        return '\n'.join(lines)

    def _mock_response(self, user_id: str, retrieved: List[Dict]) -> str:
        """Generate mock response when no LLM is available."""
        import random
        if retrieved:
            return retrieved[random.randint(0, min(2, len(retrieved)-1))]['response']
        return "hey" if self.user_profiles[user_id].capitalization == 'lowercase' else "Hey!"

    def simulate_conversation(
        self,
        user_a_id: str,
        user_b_id: str,
        starter_message: str,
        num_exchanges: int = 10,
        temperature: float = 0.9,
        verbose: bool = True
    ) -> List[Dict]:
        """
        Simulate a full conversation between two users.
        """
        conversation = [
            {"sender": user_a_id, "text": starter_message}
        ]

        if verbose:
            print("=" * 50)
            print("CONVERSATION SIMULATION")
            print("=" * 50)
            print(f"\n{user_a_id}: {starter_message}")

        for i in range(num_exchanges):
            # User B responds
            response_b = self.generate_response(
                user_b_id,
                conversation,
                temperature=temperature
            )
            conversation.append({
                "sender": user_b_id,
                "text": response_b
            })
            if verbose:
                print(f"{user_b_id}: {response_b}")

            # User A responds
            response_a = self.generate_response(
                user_a_id,
                conversation,
                temperature=temperature
            )
            conversation.append({
                "sender": user_a_id,
                "text": response_a
            })
            if verbose:
                print(f"{user_a_id}: {response_a}")

        if verbose:
            print("\n" + "=" * 50)
            print(f"Conversation complete: {len(conversation)} messages")
            print("=" * 50)

        return conversation

    def export_conversation(self, conversation: List[Dict]) -> Dict:
        """Export conversation with metadata for frontend."""
        return {
            "messages": conversation,
            "participants": list(set(msg['sender'] for msg in conversation)),
            "profiles": {
                user_id: {
                    "avg_length": self.user_profiles[user_id].avg_length,
                    "capitalization": self.user_profiles[user_id].capitalization,
                    "punctuation_style": self.user_profiles[user_id].punctuation_style,
                    "uses_emojis": self.user_profiles[user_id].uses_emojis,
                }
                for user_id in set(msg['sender'] for msg in conversation)
                if user_id in self.user_profiles
            },
            "message_count": len(conversation)
        }


# ============================================================================
# DEMO / MAIN
# ============================================================================

def main():
    """Run the vector-based conversation simulator."""

    print("=" * 60)
    print("VECTOR-BASED CONVERSATION SIMULATOR")
    print("=" * 60)
    print()

    # Initialize simulator
    simulator = VectorConversationSimulator(llm_provider="openai")

    # Check for real iMessage files
    user_a_file = "../my_texts.json"  # First user's messages
    user_b_file = "../my_texts_user2.json"  # Second user's messages (hypothetical)

    # For demo, we'll use mock data if files don't exist
    if os.path.exists(user_a_file):
        simulator.setup_user_from_file("rutva", user_a_file)
    else:
        print("Note: Using mock data (no iMessage file found)")
        # Fall back to mock data
        from conversation_simulator import create_mock_messages
        mock_data = create_mock_messages()
        simulator.setup_user("rutva", mock_data["user_a"])

    # For second user, use mock data for demo
    from conversation_simulator import create_mock_messages
    mock_data = create_mock_messages()
    simulator.setup_user("jordan", mock_data["user_b"])

    if not simulator.client:
        print("\n" + "!" * 60)
        print("No LLM client available - using mock responses")
        print("For real simulation, set OPENAI_API_KEY")
        print("!" * 60 + "\n")

    # Test retrieval
    print("\n" + "=" * 60)
    print("VECTOR SEARCH TEST")
    print("=" * 60)

    test_context = "Them: want to hang out tonight?"
    print(f"\nQuery: {test_context}\n")

    for user_id in ["rutva"]:
        if user_id in simulator.user_profiles:
            retrieved = simulator.retrieve_similar_messages(
                user_id,
                test_context,
                top_k=3
            )
            print(f"Top 3 similar messages for {user_id}:")
            for i, ex in enumerate(retrieved, 1):
                print(f"  {i}. Response: {ex['response']}")
                print(f"     Similarity: {ex['similarity']:.3f}")
            print()

    # Simulate conversation
    print("\n" + "=" * 60)
    print("STARTING CONVERSATION SIMULATION")
    print("=" * 60 + "\n")

    conversation = simulator.simulate_conversation(
        user_a_id="rutva",
        user_b_id="jordan",
        starter_message="hey what are you up to tonight",
        num_exchanges=5,
        temperature=0.9
    )

    print("\n")

    # Export for frontend
    exported = simulator.export_conversation(conversation)
    print("Exported conversation data:")
    print(json.dumps(exported, indent=2))


if __name__ == "__main__":
    main()
