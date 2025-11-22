#!/usr/bin/env python3
"""
Simulate a conversation between two people using their text message history.
Takes two my_texts.json files and creates a realistic conversation by interleaving messages.
Usage: python simulate_conversation.py <your_texts.json> <friend_texts.json> [output.json]
"""

import json
import sys
import random
from datetime import datetime, timedelta


def load_texts(filepath):
    """Load texts from a JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        texts = json.load(f)

    # Filter out empty messages and system artifacts
    filtered = []
    for text in texts:
        if text and isinstance(text, str) and not text.startswith('&__kIM'):
            filtered.append(text.strip())

    return filtered


def simulate_conversation(person1_texts, person2_texts, num_messages=50, person1_name="Person 1", person2_name="Person 2"):
    """
    Simulate a conversation by alternating between two sets of messages.

    Args:
        person1_texts: List of text messages from person 1
        person2_texts: List of text messages from person 2
        num_messages: Total number of messages in the simulated conversation
        person1_name: Display name for person 1
        person2_name: Display name for person 2

    Returns:
        List of message objects for the conversation
    """
    conversation = []

    # Start timestamp (some time in the past)
    current_time = datetime.now() - timedelta(days=7)

    # Randomly pick starting person
    person1_turn = random.choice([True, False])

    # Keep track of indices
    p1_idx = 0
    p2_idx = 0

    for i in range(num_messages):
        # Decide who sends this message
        if person1_turn:
            if p1_idx < len(person1_texts):
                sender = person1_name
                text = person1_texts[p1_idx]
                is_from_me = True
                p1_idx += 1
            else:
                # Ran out of person 1's messages, switch to person 2
                person1_turn = False
                continue
        else:
            if p2_idx < len(person2_texts):
                sender = person2_name
                text = person2_texts[p2_idx]
                is_from_me = False
                p2_idx += 1
            else:
                # Ran out of person 2's messages, switch to person 1
                person1_turn = True
                continue

        # Add message to conversation
        conversation.append({
            "id": i + 1,
            "sender": sender,
            "is_from_me": is_from_me,
            "text": text,
            "timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        })

        # Randomly advance time (between 30 seconds and 10 minutes)
        time_delta = timedelta(seconds=random.randint(30, 600))
        current_time += time_delta

        # Randomly switch turns (70% chance to continue same person, 30% to switch)
        # This creates more realistic back-and-forth
        if random.random() < 0.3:
            person1_turn = not person1_turn

    return conversation


def main():
    if len(sys.argv) < 3:
        print("Usage: python simulate_conversation.py <your_texts.json> <friend_texts.json> [output.json] [num_messages]")
        print("Example: python simulate_conversation.py my_texts.json friend_texts.json conversation.json 100")
        sys.exit(1)

    your_texts_file = sys.argv[1]
    friend_texts_file = sys.argv[2]
    output_file = sys.argv[3] if len(sys.argv) > 3 else "simulated_conversation.json"
    num_messages = int(sys.argv[4]) if len(sys.argv) > 4 else 50

    print(f"Loading your texts from: {your_texts_file}")
    your_texts = load_texts(your_texts_file)
    print(f"  → Loaded {len(your_texts)} messages")

    print(f"Loading friend's texts from: {friend_texts_file}")
    friend_texts = load_texts(friend_texts_file)
    print(f"  → Loaded {len(friend_texts)} messages")

    print(f"\nSimulating conversation with {num_messages} messages...")

    # Get names from user
    your_name = input("Your name (default: You): ").strip() or "You"
    friend_name = input("Friend's name (default: Friend): ").strip() or "Friend"

    # Simulate the conversation
    conversation = simulate_conversation(
        your_texts,
        friend_texts,
        num_messages=num_messages,
        person1_name=your_name,
        person2_name=friend_name
    )

    # Create output structure
    output = {
        "conversation_id": 1,
        "participants": [your_name, friend_name],
        "message_count": len(conversation),
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "messages": conversation
    }

    # Save to file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Conversation saved to: {output_file}")
    print(f"  → {len(conversation)} messages")
    print(f"  → Between {your_name} and {friend_name}")

    # Preview first few messages
    print("\nPreview of conversation:")
    print("=" * 60)
    for msg in conversation[:5]:
        print(f"[{msg['timestamp']}] {msg['sender']}:")
        print(f"  {msg['text']}")
        print()
    print("...")


if __name__ == "__main__":
    main()
