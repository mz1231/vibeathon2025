"""
Conversation Simulator with LLM Integration
=============================================
Production-ready version with actual OpenAI/Anthropic integration.
"""

import os
import json
import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
import re
from collections import Counter

# Import the base simulator
from conversation_simulator import (
    UserProfile,
    MockVectorDB,
    analyze_user_style,
    store_user_messages,
    retrieve_similar_messages,
    build_prompt,
    format_conversation,
    create_mock_messages,
)


class ConversationSimulatorLLM:
    """
    Conversation simulator with real LLM integration.
    Supports OpenAI GPT-4 and Anthropic Claude.
    """

    def __init__(self, llm_provider: str = "openai"):
        """
        Initialize the simulator.

        Args:
            llm_provider: "openai" or "anthropic"
        """
        self.vector_db = MockVectorDB()
        self.user_profiles: Dict[str, UserProfile] = {}
        self.messages_data: Dict[str, List[Dict]] = {}
        self.llm_provider = llm_provider

        # Initialize LLM client
        self.client = None
        if llm_provider == "openai":
            try:
                from openai import OpenAI
                api_key = os.environ.get("OPENAI_API_KEY")
                if api_key:
                    self.client = OpenAI(api_key=api_key)
                    self.embedding_model = "text-embedding-3-small"
                    self.chat_model = "gpt-4"
                else:
                    print("Note: OPENAI_API_KEY not set. Using mock responses.")
            except ImportError:
                print("Warning: openai not installed. Run: pip install openai")
        elif llm_provider == "anthropic":
            try:
                import anthropic
                api_key = os.environ.get("ANTHROPIC_API_KEY")
                if api_key:
                    self.client = anthropic.Anthropic(api_key=api_key)
                    self.chat_model = "claude-3-5-sonnet-20241022"
                else:
                    print("Note: ANTHROPIC_API_KEY not set. Using mock responses.")
            except ImportError:
                print("Warning: anthropic not installed. Run: pip install anthropic")
        else:
            raise ValueError(f"Unknown provider: {llm_provider}")

    def create_embedding(self, text: str) -> np.ndarray:
        """Create an embedding using OpenAI's API."""
        if self.llm_provider == "openai" and self.client:
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            return np.array(response.data[0].embedding)
        else:
            # Fallback to mock embedding
            from conversation_simulator import create_embedding
            return create_embedding(text)

    def setup_user(self, user_id: str, messages: List[Dict]):
        """
        Initialize a user with their message history.
        """
        self.messages_data[user_id] = messages

        # Analyze user style
        profile = analyze_user_style(messages)
        profile.user_id = user_id
        self.user_profiles[user_id] = profile

        # Store embeddings
        store_user_messages(self.vector_db, user_id, messages)

        print(f"Setup complete for {user_id}:")
        print(f"  - Avg message length: {profile.avg_length}")
        print(f"  - Capitalization: {profile.capitalization}")
        print(f"  - Uses emojis: {profile.uses_emojis}")
        print(f"  - Punctuation: {profile.punctuation_style}")
        print()

    def generate_response(
        self,
        user_id: str,
        conversation_history: List[Dict],
        top_k: int = 8,
        temperature: float = 0.8
    ) -> str:
        """
        Generate a response using actual LLM.
        """
        # Format recent conversation
        recent_messages = conversation_history[-6:] if len(conversation_history) > 6 else conversation_history
        current_context = format_conversation(recent_messages)

        # Retrieve similar examples
        retrieved = retrieve_similar_messages(
            self.vector_db,
            user_id,
            current_context,
            top_k=top_k
        )

        # Get user profile
        user_profile = self.user_profiles[user_id]

        # Build prompt
        prompt = build_prompt(user_profile, retrieved, current_context)

        # Generate with LLM
        if self.llm_provider == "openai" and self.client:
            response = self.client.chat.completions.create(
                model=self.chat_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=150
            )
            return response.choices[0].message.content.strip()

        elif self.llm_provider == "anthropic" and self.client:
            response = self.client.messages.create(
                model=self.chat_model,
                max_tokens=150,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text.strip()

        else:
            # Fallback to mock response
            return self._mock_response(user_profile, retrieved)

    def _mock_response(
        self,
        user_profile: UserProfile,
        retrieved_examples: List[Dict]
    ) -> str:
        """Generate a mock response when no LLM is available."""
        import random

        if not retrieved_examples:
            if user_profile.capitalization == 'lowercase':
                return "hey! what's up"
            else:
                return "Hey! How's it going?"

        # Pick from top examples with some randomness
        idx = random.randint(0, min(2, len(retrieved_examples) - 1))
        return retrieved_examples[idx]['response']

    def simulate_conversation(
        self,
        user_a_id: str,
        user_b_id: str,
        starter_message: str,
        num_exchanges: int = 10,
        temperature: float = 0.8
    ) -> List[Dict]:
        """
        Simulate a full conversation between two users.
        """
        conversation = [
            {"sender": user_a_id, "text": starter_message}
        ]

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

        return conversation

    def export_for_frontend(
        self,
        conversation: List[Dict],
        include_metadata: bool = True
    ) -> Dict:
        """
        Export conversation data in a format suitable for frontend display.
        """
        output = {
            "messages": conversation,
            "user_profiles": {}
        }

        if include_metadata:
            for user_id in set(msg['sender'] for msg in conversation):
                if user_id in self.user_profiles:
                    profile = self.user_profiles[user_id]
                    output["user_profiles"][user_id] = {
                        "avg_length": profile.avg_length,
                        "uses_emojis": profile.uses_emojis,
                        "capitalization": profile.capitalization,
                        "punctuation_style": profile.punctuation_style,
                        "common_phrases": profile.common_phrases
                    }

        return output


# ============================================================================
# API-READY FUNCTIONS
# ============================================================================

def create_simulator_from_json(user_data: Dict[str, List[Dict]], llm_provider: str = "openai") -> ConversationSimulatorLLM:
    """
    Create a simulator from JSON message data.

    Args:
        user_data: Dictionary mapping user_id to list of messages
        llm_provider: "openai" or "anthropic"

    Returns:
        Configured ConversationSimulatorLLM instance
    """
    simulator = ConversationSimulatorLLM(llm_provider)

    for user_id, messages in user_data.items():
        simulator.setup_user(user_id, messages)

    return simulator


def simulate_single_response(
    simulator: ConversationSimulatorLLM,
    user_id: str,
    conversation_history: List[Dict]
) -> Dict:
    """
    Generate a single response (API endpoint format).

    Returns:
        {
            "response": "the generated message",
            "user_profile": {...},
            "retrieved_examples": [...]
        }
    """
    # Get response
    response = simulator.generate_response(user_id, conversation_history)

    # Get metadata
    recent_messages = conversation_history[-6:] if len(conversation_history) > 6 else conversation_history
    current_context = format_conversation(recent_messages)

    retrieved = retrieve_similar_messages(
        simulator.vector_db,
        user_id,
        current_context,
        top_k=3
    )

    profile = simulator.user_profiles.get(user_id)

    return {
        "response": response,
        "user_profile": {
            "avg_length": profile.avg_length if profile else 0,
            "capitalization": profile.capitalization if profile else "mixed",
            "uses_emojis": profile.uses_emojis if profile else False,
        },
        "retrieved_examples": [
            {"context": ex['context'], "response": ex['response']}
            for ex in retrieved[:3]
        ]
    }


# ============================================================================
# EXAMPLE WITH REAL LLM
# ============================================================================

def run_llm_demo():
    """Run demo with actual LLM integration."""

    print("=" * 60)
    print("CONVERSATION SIMULATOR WITH LLM")
    print("=" * 60)
    print()

    # Check for API key
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Note: OPENAI_API_KEY not set. Using mock responses.")
        print("Set the key to use actual LLM generation:")
        print("  export OPENAI_API_KEY='your-key-here'")
        print()

    # Initialize simulator
    simulator = ConversationSimulatorLLM("openai")

    # Load mock data
    mock_data = create_mock_messages()

    # Setup users
    simulator.setup_user("user_a", mock_data["user_a"])
    simulator.setup_user("user_b", mock_data["user_b"])

    # Test single response
    print("=" * 60)
    print("SINGLE RESPONSE TEST")
    print("=" * 60)
    print()

    conversation_so_far = [
        {"sender": "user_a", "text": "hey are you coming to the party tonight"},
        {"sender": "user_b", "text": "what party?"},
        {"sender": "user_a", "text": "mike's birthday at his place"},
    ]

    print("Conversation:")
    for msg in conversation_so_far:
        print(f"  {msg['sender']}: {msg['text']}")
    print()

    result = simulate_single_response(simulator, "user_b", conversation_so_far)
    print(f"user_b's response: {result['response']}")
    print(f"Based on {len(result['retrieved_examples'])} similar examples")
    print()

    # Full conversation
    print("=" * 60)
    print("FULL CONVERSATION")
    print("=" * 60)
    print()

    conversation = simulator.simulate_conversation(
        "user_a",
        "user_b",
        "hey wanna hang out tonight?",
        num_exchanges=3
    )

    for msg in conversation:
        print(f"{msg['sender']}: {msg['text']}")

    print()

    # Export for frontend
    exported = simulator.export_for_frontend(conversation)
    print("Exported JSON for frontend:")
    print(json.dumps(exported, indent=2)[:500] + "...")


if __name__ == "__main__":
    run_llm_demo()
