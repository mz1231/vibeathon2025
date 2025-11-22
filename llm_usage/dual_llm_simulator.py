"""
Dual LLM Conversation Simulator
================================
Two LLMs chat with each other, each simulating a different user's texting style
based on their message history and RAG-retrieved examples.
"""

import os
import json
import numpy as np
from typing import List, Dict, Optional
from dataclasses import dataclass

from conversation_simulator import (
    UserProfile,
    MockVectorDB,
    analyze_user_style,
    store_user_messages,
    retrieve_similar_messages,
    format_conversation,
    create_embedding,
)


class DualLLMSimulator:
    """
    Simulates conversations between two users, each powered by an LLM
    that mimics their texting style using RAG.
    """

    def __init__(self, llm_provider: str = "openai"):
        """
        Initialize the dual LLM simulator.

        Args:
            llm_provider: "openai" or "anthropic"
        """
        self.vector_db = MockVectorDB()
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
                    self.client = OpenAI(api_key=api_key.strip())
                    self.chat_model = "gpt-4.1-mini"
                else:
                    print("Warning: OPENAI_API_KEY not set.")
                    print("Set it with: export OPENAI_API_KEY='your-key'")
            except ImportError:
                print("Warning: openai not installed. Run: pip install openai")

        elif self.llm_provider == "anthropic":
            try:
                import anthropic
                api_key = os.environ.get("ANTHROPIC_API_KEY")
                if api_key:
                    self.client = anthropic.Anthropic(api_key=api_key)
                    self.chat_model = "claude-3-5-sonnet-20241022"
                else:
                    print("Warning: ANTHROPIC_API_KEY not set.")
                    print("Set it with: export ANTHROPIC_API_KEY='your-key'")
            except ImportError:
                print("Warning: anthropic not installed. Run: pip install anthropic")

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

        # Store embeddings in vector DB
        store_user_messages(self.vector_db, user_id, messages)

        print(f"User '{user_id}' initialized:")
        print(f"  - {len(messages)} messages indexed")
        print(f"  - Avg length: {profile.avg_length} chars")
        print(f"  - Style: {profile.capitalization}, {profile.punctuation_style}")
        print()

    def _build_system_prompt(self, user_id: str) -> str:
        """Build a system prompt for the LLM to adopt the user's persona."""
        profile = self.user_profiles[user_id]

        return f"""You are simulating how a specific person texts. You must respond EXACTLY as they would - matching their texting style perfectly.
IMPORTANT:
- REALLY match THEIR SPECIFIC tone, energy, slang, AND PERSONALITY
- Keep responses natural and conversational
- Respond with ONLY the message text, nothing extra"""

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

    def generate_response(
        self,
        user_id: str,
        conversation_history: List[Dict],
        temperature: float = 0.9
    ) -> str:
        """
        Generate a response for the specified user using LLM.

        Args:
            user_id: The user to simulate
            conversation_history: List of previous messages
            temperature: LLM temperature for response variation

        Returns:
            Generated response text
        """
        # Get recent context for retrieval
        recent = conversation_history[-4:] if len(conversation_history) > 4 else conversation_history
        context_for_retrieval = format_conversation(recent)

        # Retrieve similar examples from this user's history
        retrieved = retrieve_similar_messages(
            self.vector_db,
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

        Each turn:
        1. User A's LLM generates based on A's style + retrieved examples
        2. User B's LLM generates based on B's style + retrieved examples

        Args:
            user_a_id: First user (starts the conversation)
            user_b_id: Second user
            starter_message: Opening message from user_a
            num_exchanges: Number of back-and-forth exchanges
            temperature: LLM temperature
            verbose: Print messages as they're generated

        Returns:
            List of message dictionaries
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

    def simulate_with_topic(
        self,
        user_a_id: str,
        user_b_id: str,
        topic: str,
        num_exchanges: int = 10,
        temperature: float = 0.9,
        verbose: bool = True
    ) -> List[Dict]:
        """
        Simulate a conversation about a specific topic.

        Args:
            user_a_id: First user
            user_b_id: Second user
            topic: What they should talk about
            num_exchanges: Number of exchanges
            temperature: LLM temperature
            verbose: Print messages

        Returns:
            List of messages
        """
        # Generate a starter message in user_a's style about the topic
        profile_a = self.user_profiles[user_a_id]

        if self.client and self.llm_provider == "openai":
            starter_prompt = f"""Generate a short opening text message about going out plans: {topic}

Style rules:

Make sure to EXACTLY use this person's texting style, including unique words and slang that they historically show in their text messages. Really capture their personality.

Respond with ONLY the message text."""

            response = self.client.chat.completions.create(
                model=self.chat_model,
                messages=[{"role": "user", "content": starter_prompt}],
                temperature=temperature,
                max_tokens=50
            )
            starter = response.choices[0].message.content.strip()
        else:
            # Fallback starters based on style
            if profile_a.capitalization == 'lowercase':
                starter = f"hey wanna talk about {topic}?"
            else:
                starter = f"Hey! Want to discuss {topic}?"

        return self.simulate_conversation(
            user_a_id,
            user_b_id,
            starter,
            num_exchanges,
            temperature,
            verbose
        )

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

def load_user_messages_from_json(file_path: str) -> List[Dict]:
    """
    Load messages from a JSON file and convert to the required format.

    The JSON files contain arrays of standalone messages. We convert them
    to context/response pairs by pairing consecutive messages.
    """
    with open(file_path, 'r') as f:
        messages = json.load(f)

    # Convert standalone messages to context/response format
    formatted_messages = []
    for i in range(1, len(messages)):
        # Use previous message as context, current as response
        formatted_messages.append({
            "context": f"Them: {messages[i-1]}",
            "response": messages[i],
            "timestamp": f"2025-01-{(i % 28) + 1:02d}T{(i % 24):02d}:00:00"
        })

    return formatted_messages


def main():
    """Run the dual LLM conversation simulator."""

    print("=" * 60)
    print("DUAL LLM CONVERSATION SIMULATOR")
    print("=" * 60)
    print()

    # Initialize simulator
    simulator = DualLLMSimulator(llm_provider="openai")

    # Load real user data from JSON files
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)

    user_a_path = os.path.join(project_dir, "user_a.json")
    user_b_path = os.path.join(project_dir, "user_b.json")

    user_a_messages = load_user_messages_from_json(user_a_path)
    user_b_messages = load_user_messages_from_json(user_b_path)

    print(f"Loaded {len(user_a_messages)} messages for user_a")
    print(f"Loaded {len(user_b_messages)} messages for user_b")
    print()

    # Setup both users
    simulator.setup_user("Rutva", user_a_messages)
    simulator.setup_user("Zaeem", user_b_messages)

    if not simulator.client:
        print("\n" + "!" * 60)
        print("No LLM client available - using mock responses")
        print("For real simulation, set OPENAI_API_KEY or ANTHROPIC_API_KEY")
        print("!" * 60 + "\n")

    # Simulate conversation
    conversation = simulator.simulate_conversation(
        user_a_id="Rutva",
        user_b_id="Zaeem",
        starter_message="hey wanna hang out tonight?",
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