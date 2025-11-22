#!/usr/bin/env python3
"""
Simulate a conversation between two LLMs trained on different people's text styles.
Each LLM generates responses based on the messaging patterns from their respective datasets.
Usage: python llm_conversation_simulator.py <person1_texts.json> <person2_texts.json> [num_messages] [output.json]
"""

import json
import sys
import os
from datetime import datetime, timedelta
import random

try:
    from openai import OpenAI
except ImportError:
    print("Error: openai package not installed. Install with: pip install openai")
    sys.exit(1)


def load_texts(filepath):
    """Load texts from a JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        texts = json.load(f)

    # Filter out empty messages and system artifacts
    filtered = []
    for text in texts:
        if text and isinstance(text, str) and not text.startswith('&__kIM') and not text.startswith('__kIM') and text != '￼':
            filtered.append(text.strip())

    return filtered


def create_persona_prompt(texts, person_name):
    """Create a prompt that captures the person's texting style."""
    # Sample some representative texts
    sample_size = min(100, len(texts))
    sample_texts = random.sample(texts, sample_size)

    prompt = f"""You are simulating {person_name}'s texting style. Here are examples of how {person_name} texts:

Examples:
{chr(10).join(f'- "{text}"' for text in sample_texts[:50])}

Key characteristics to emulate:
- Use similar vocabulary, slang, and expressions
- Match the tone (casual, formal, enthusiastic, etc.)
- Use similar punctuation and emoji patterns
- Keep responses concise like text messages (1-3 sentences max)
- Use abbreviations and shortcuts similar to the examples
- Match the energy level and capitalization patterns

You are now {person_name} in a conversation. Respond naturally as {person_name} would, staying in character. Keep responses SHORT and conversational."""

    return prompt


def generate_response(client, persona_prompt, conversation_history, person_name):
    """Generate a response from the LLM based on the persona and conversation history."""

    # Build conversation context
    messages = [
        {"role": "system", "content": persona_prompt}
    ]

    # Add conversation history (last 10 messages for context)
    for msg in conversation_history[-10:]:
        if msg['sender'] == person_name:
            messages.append({
                "role": "assistant",
                "content": msg['text']
            })
        else:
            messages.append({
                "role": "user",
                "content": msg['text']
            })

    # If no history or last message was from this person, add a prompt to start
    if len(messages) == 1:  # Only system prompt
        messages.append({
            "role": "user",
            "content": "Hey what's up"
        })
    elif messages[-1]["role"] == "assistant":
        messages.append({
            "role": "user",
            "content": "Continue the conversation naturally with a short response."
        })

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # or "gpt-4" for better quality
            messages=messages,
            max_tokens=100,
            temperature=0.9,  # Higher temperature for more variety
        )

        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error generating response: {e}")
        return "Hey what's up"


def simulate_llm_conversation(person1_texts, person2_texts, num_messages=20,
                              person1_name="Person 1", person2_name="Person 2",
                              api_key=None):
    """
    Simulate a conversation between two LLMs trained on different texting styles.
    """

    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set")
        sys.exit(1)

    client = OpenAI(api_key=api_key)

    # Create persona prompts
    print("Creating persona prompts...")
    person1_prompt = create_persona_prompt(person1_texts, person1_name)
    person2_prompt = create_persona_prompt(person2_texts, person2_name)

    conversation = []
    current_time = datetime.now() - timedelta(hours=2)

    # Randomly pick who starts
    current_speaker = random.choice([person1_name, person2_name])

    print(f"\nSimulating {num_messages}-message conversation between {person1_name} and {person2_name}...")
    print("=" * 60)

    for i in range(num_messages):
        # Determine who's speaking
        if current_speaker == person1_name:
            prompt = person1_prompt
            is_from_me = True
        else:
            prompt = person2_prompt
            is_from_me = False

        # Generate response
        print(f"\n[{i+1}/{num_messages}] Generating response from {current_speaker}...")
        text = generate_response(client, prompt, conversation, current_speaker)

        # Add to conversation
        message = {
            "id": i + 1,
            "sender": current_speaker,
            "is_from_me": is_from_me,
            "text": text,
            "timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S")
        }
        conversation.append(message)

        print(f"{current_speaker}: {text}")

        # Advance time (30 seconds to 5 minutes)
        time_delta = timedelta(seconds=random.randint(30, 300))
        current_time += time_delta

        # Switch speakers
        current_speaker = person2_name if current_speaker == person1_name else person1_name

    print("\n" + "=" * 60)
    print(f"✓ Generated {len(conversation)} messages")

    return conversation


def main():
    if len(sys.argv) < 3:
        print("Usage: python llm_conversation_simulator.py <person1_texts.json> <person2_texts.json> [num_messages] [output.json]")
        print("Example: python llm_conversation_simulator.py my_texts.json friend_texts.json 20 conversation.json")
        print("\nNote: Requires OPENAI_API_KEY environment variable to be set")
        sys.exit(1)

    person1_file = sys.argv[1]
    person2_file = sys.argv[2]
    num_messages = int(sys.argv[3]) if len(sys.argv) > 3 else 20
    output_file = sys.argv[4] if len(sys.argv) > 4 else "llm_conversation.json"

    # Check for API key
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set")
        print("Set it with: export OPENAI_API_KEY='your-key-here'")
        sys.exit(1)

    print(f"Loading texts from {person1_file}...")
    person1_texts = load_texts(person1_file)
    print(f"  → Loaded {len(person1_texts)} messages")

    print(f"Loading texts from {person2_file}...")
    person2_texts = load_texts(person2_file)
    print(f"  → Loaded {len(person2_texts)} messages")

    # Get names
    person1_name = input("\nPerson 1 name (default: Richard): ").strip() or "Richard"
    person2_name = input("Person 2 name (default: Friend): ").strip() or "Friend"

    # Generate conversation
    conversation = simulate_llm_conversation(
        person1_texts,
        person2_texts,
        num_messages=num_messages,
        person1_name=person1_name,
        person2_name=person2_name,
        api_key=api_key
    )

    # Create output structure
    output = {
        "conversation_id": 1,
        "participants": [person1_name, person2_name],
        "message_count": len(conversation),
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "generation_method": "llm_simulation",
        "messages": conversation
    }

    # Save to file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Conversation saved to: {output_file}")
    print(f"  → {len(conversation)} messages")
    print(f"  → Between {person1_name} and {person2_name}")

    # Preview
    print("\nPreview:")
    print("=" * 60)
    for msg in conversation[:5]:
        print(f"[{msg['timestamp']}] {msg['sender']}:")
        print(f"  {msg['text']}")
        print()
    if len(conversation) > 5:
        print("...")


if __name__ == "__main__":
    main()
