#!/usr/bin/env python3
"""
Run the dual LLM simulator with actual user JSON files.
"""

import json
import sys
import os

# Add the llm_usage directory to path
sys.path.insert(0, '/Users/rutvashah/Vibeathon/vibeathon2025/llm_usage')

from conversation_simulator import (
    UserProfile,
    MockVectorDB,
    analyze_user_style,
    store_user_messages,
    retrieve_similar_messages,
    format_conversation,
    create_embedding,
)
from dual_llm_simulator import DualLLMSimulator


def load_user_texts(filepath):
    """Load texts from a JSON file and convert to message format."""
    with open(filepath, 'r', encoding='utf-8') as f:
        texts = json.load(f)

    # Filter out empty messages and system artifacts
    filtered = []
    for i, text in enumerate(texts):
        if text and isinstance(text, str):
            # Skip system artifacts
            if text.startswith('&__kIM') or text.startswith('__kIM') or text == '￼':
                continue
            if 'NSURL' in text or text.startswith('$'):
                continue
            cleaned = text.strip()
            if cleaned:
                filtered.append(cleaned)

    return filtered


def convert_texts_to_messages(texts):
    """Convert a list of text strings into message format for the simulator."""
    messages = []

    # Create context-response pairs
    # We'll use the texts as responses to various generic contexts
    contexts = [
        "Them: hey what's up",
        "Them: what are you doing",
        "Them: want to hang out",
        "Them: did you see that",
        "Them: how's it going",
        "Them: what do you think",
        "Them: are you free",
        "Them: check this out",
        "Them: lol",
        "Them: nice",
        "Them: ok",
        "Them: sounds good",
    ]

    for i, text in enumerate(texts):
        context = contexts[i % len(contexts)]
        messages.append({
            "context": context,
            "response": text,
            "timestamp": f"2025-01-{(i % 28) + 1:02d}T{(i % 24):02d}:00:00"
        })

    return messages


def main():
    print("=" * 60)
    print("DUAL LLM CONVERSATION SIMULATOR")
    print("=" * 60)
    print()

    # Load user texts from JSON files
    user_a_path = "/Users/rutvashah/Vibeathon/vibeathon2025/user_a.json"
    user_b_path = "/Users/rutvashah/Vibeathon/vibeathon2025/user_b.json"

    print(f"Loading user A texts from {user_a_path}...")
    user_a_texts = load_user_texts(user_a_path)
    print(f"  → Loaded {len(user_a_texts)} messages")

    print(f"Loading user B texts from {user_b_path}...")
    user_b_texts = load_user_texts(user_b_path)
    print(f"  → Loaded {len(user_b_texts)} messages")
    print()

    # Convert to message format
    user_a_messages = convert_texts_to_messages(user_a_texts)
    user_b_messages = convert_texts_to_messages(user_b_texts)

    # Initialize simulator
    print("Initializing LLM simulator...")
    simulator = DualLLMSimulator(llm_provider="openai")

    # Setup both users
    print("\nSetting up users...")
    simulator.setup_user("Rutva", user_a_messages)
    simulator.setup_user("Friend", user_b_messages)

    if not simulator.client:
        print("\n" + "!" * 60)
        print("No LLM client available - using mock responses")
        print("For real simulation, set OPENAI_API_KEY:")
        print("  export OPENAI_API_KEY='your-key'")
        print("!" * 60 + "\n")
    else:
        print("\n✓ OpenAI client initialized successfully")

    # Simulate conversation
    print("\nStarting conversation simulation...")
    print("-" * 60)

    conversation = simulator.simulate_conversation(
        user_a_id="Rutva",
        user_b_id="Friend",
        starter_message="hey wanna hang out tonight?",
        num_exchanges=8,
        temperature=0.9
    )

    print()

    # Export for frontend
    exported = simulator.export_conversation(conversation)

    # Save to file
    output_file = "/Users/rutvashah/Vibeathon/vibeathon2025/simulated_conversation.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(exported, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Conversation saved to: {output_file}")
    print(f"  → {len(conversation)} messages generated")

    # Print summary
    print("\nConversation Summary:")
    print(json.dumps(exported, indent=2))


if __name__ == "__main__":
    main()
