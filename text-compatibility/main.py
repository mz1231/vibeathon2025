#!/usr/bin/env python3
"""
Text Compatibility - Main Pipeline
==================================

This script demonstrates the complete flow:
1. Parse messages (from JSON or iMessage)
2. Create embeddings using OpenAI
3. Store in ChromaDB vector database
4. Retrieve relevant context for new conversations

SETUP:
------
1. Set your OpenAI API key:
   export OPENAI_API_KEY="your-api-key-here"

2. Run this script:
   python main.py

The script will:
- Create sample conversation data
- Build embeddings for each user
- Store them in a local ChromaDB database
- Demonstrate retrieval with test queries
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from message_parser import (
    JSONParser,
    create_message_windows,
    create_sample_data,
    Message,
    MessageWindow
)
from embeddings import OpenAIEmbedder, cosine_similarity
from vector_store import VectorStore, RAGPipeline


def check_api_key():
    """Verify OpenAI API key is set."""
    api_key = os.environ.get('OPENAI_API_KEY')
    
    if not api_key:
        print("=" * 60)
        print("ERROR: OPENAI_API_KEY not found!")
        print("=" * 60)
        print()
        print("Please set your API key in the terminal:")
        print()
        print("  export OPENAI_API_KEY='sk-your-key-here'")
        print()
        print("Then run this script again.")
        print("=" * 60)
        sys.exit(1)
    
    # Show partial key for verification
    masked_key = api_key[:7] + "..." + api_key[-4:]
    print(f"✓ API Key found: {masked_key}")
    return api_key


def create_extended_sample_data():
    """
    Create a more extensive sample dataset with two users.
    
    This simulates a conversation between Alice and Bob,
    with enough messages to demonstrate meaningful retrieval.
    """
    return {
        "conversation_id": "alice_bob_001",
        "participants": ["alice", "bob"],
        "messages": [
            # Conversation 1: Making plans
            {"id": "1", "sender_id": "alice", "text": "hey! what are you up to tonight?", "timestamp": "2025-01-15T18:00:00Z"},
            {"id": "2", "sender_id": "bob", "text": "not much, probably just staying in. why?", "timestamp": "2025-01-15T18:02:00Z"},
            {"id": "3", "sender_id": "alice", "text": "want to grab dinner? I'm craving thai food", "timestamp": "2025-01-15T18:03:00Z"},
            {"id": "4", "sender_id": "bob", "text": "ooh yes! that sounds amazing actually", "timestamp": "2025-01-15T18:04:00Z"},
            {"id": "5", "sender_id": "alice", "text": "perfect! how about that new place on Main St?", "timestamp": "2025-01-15T18:04:30Z"},
            {"id": "6", "sender_id": "bob", "text": "I've been wanting to try that! 7pm work?", "timestamp": "2025-01-15T18:05:00Z"},
            {"id": "7", "sender_id": "alice", "text": "yes!! see you there 🍜", "timestamp": "2025-01-15T18:05:30Z"},
            
            # Conversation 2: School/work talk
            {"id": "8", "sender_id": "bob", "text": "ugh this assignment is killing me", "timestamp": "2025-01-16T14:00:00Z"},
            {"id": "9", "sender_id": "alice", "text": "which one? the CS project?", "timestamp": "2025-01-16T14:05:00Z"},
            {"id": "10", "sender_id": "bob", "text": "yeah, I can't figure out the algorithm part", "timestamp": "2025-01-16T14:06:00Z"},
            {"id": "11", "sender_id": "alice", "text": "want me to help? I finished mine yesterday", "timestamp": "2025-01-16T14:07:00Z"},
            {"id": "12", "sender_id": "bob", "text": "omg yes please, you're a lifesaver", "timestamp": "2025-01-16T14:08:00Z"},
            {"id": "13", "sender_id": "alice", "text": "np! library in 30?", "timestamp": "2025-01-16T14:08:30Z"},
            {"id": "14", "sender_id": "bob", "text": "perfect, I'll bring coffee as thanks ☕", "timestamp": "2025-01-16T14:09:00Z"},
            
            # Conversation 3: Weekend plans
            {"id": "15", "sender_id": "alice", "text": "so what's the plan for saturday?", "timestamp": "2025-01-17T20:00:00Z"},
            {"id": "16", "sender_id": "bob", "text": "mike's party at 9, remember?", "timestamp": "2025-01-17T20:02:00Z"},
            {"id": "17", "sender_id": "alice", "text": "oh right! should we pregame first?", "timestamp": "2025-01-17T20:03:00Z"},
            {"id": "18", "sender_id": "bob", "text": "definitely, your place or mine?", "timestamp": "2025-01-17T20:04:00Z"},
            {"id": "19", "sender_id": "alice", "text": "mine! I got a new speaker we gotta try out", "timestamp": "2025-01-17T20:04:30Z"},
            {"id": "20", "sender_id": "bob", "text": "say less, I'll be there at 7:30", "timestamp": "2025-01-17T20:05:00Z"},
            
            # Conversation 4: Casual chat
            {"id": "21", "sender_id": "bob", "text": "did you see that new marvel movie?", "timestamp": "2025-01-18T15:00:00Z"},
            {"id": "22", "sender_id": "alice", "text": "not yet! is it good??", "timestamp": "2025-01-18T15:10:00Z"},
            {"id": "23", "sender_id": "bob", "text": "honestly it was mid, don't rush to see it", "timestamp": "2025-01-18T15:11:00Z"},
            {"id": "24", "sender_id": "alice", "text": "lol ok noted. what about that horror one?", "timestamp": "2025-01-18T15:12:00Z"},
            {"id": "25", "sender_id": "bob", "text": "ooh haven't seen it but I heard it's actually scary", "timestamp": "2025-01-18T15:13:00Z"},
            {"id": "26", "sender_id": "alice", "text": "we should go! I love being terrified 😈", "timestamp": "2025-01-18T15:14:00Z"},
            {"id": "27", "sender_id": "bob", "text": "you're weird but ok I'm down", "timestamp": "2025-01-18T15:15:00Z"},
            
            # Conversation 5: Food again
            {"id": "28", "sender_id": "alice", "text": "I'm so hungry rn", "timestamp": "2025-01-19T12:00:00Z"},
            {"id": "29", "sender_id": "bob", "text": "same, want to get lunch?", "timestamp": "2025-01-19T12:01:00Z"},
            {"id": "30", "sender_id": "alice", "text": "yes please! chipotle?", "timestamp": "2025-01-19T12:02:00Z"},
            {"id": "31", "sender_id": "bob", "text": "you read my mind. meet in 15?", "timestamp": "2025-01-19T12:03:00Z"},
            {"id": "32", "sender_id": "alice", "text": "perfect see you soon!", "timestamp": "2025-01-19T12:03:30Z"},
            
            # Conversation 6: Emotional support
            {"id": "33", "sender_id": "bob", "text": "hey, you around?", "timestamp": "2025-01-20T22:00:00Z"},
            {"id": "34", "sender_id": "alice", "text": "yeah what's up? you ok?", "timestamp": "2025-01-20T22:01:00Z"},
            {"id": "35", "sender_id": "bob", "text": "idk, just having a rough day", "timestamp": "2025-01-20T22:02:00Z"},
            {"id": "36", "sender_id": "alice", "text": "I'm sorry :( want to talk about it?", "timestamp": "2025-01-20T22:02:30Z"},
            {"id": "37", "sender_id": "bob", "text": "maybe later, can we just hang?", "timestamp": "2025-01-20T22:03:00Z"},
            {"id": "38", "sender_id": "alice", "text": "of course! want me to come over? I'll bring ice cream", "timestamp": "2025-01-20T22:03:30Z"},
            {"id": "39", "sender_id": "bob", "text": "you're the best, thank you 💙", "timestamp": "2025-01-20T22:04:00Z"},
            
            # Conversation 7: Making more plans
            {"id": "40", "sender_id": "alice", "text": "spring break is coming up!", "timestamp": "2025-01-21T16:00:00Z"},
            {"id": "41", "sender_id": "bob", "text": "I know!! any plans?", "timestamp": "2025-01-21T16:05:00Z"},
            {"id": "42", "sender_id": "alice", "text": "thinking about a beach trip, you interested?", "timestamp": "2025-01-21T16:06:00Z"},
            {"id": "43", "sender_id": "bob", "text": "um YES absolutely count me in", "timestamp": "2025-01-21T16:07:00Z"},
            {"id": "44", "sender_id": "alice", "text": "yay!! I'll start looking at airbnbs", "timestamp": "2025-01-21T16:07:30Z"},
            {"id": "45", "sender_id": "bob", "text": "let me know the budget and I'm there", "timestamp": "2025-01-21T16:08:00Z"},
        ]
    }


def run_pipeline():
    """
    Run the complete pipeline demonstration.
    
    This shows exactly how all the pieces connect:
    1. Parse messages from JSON
    2. Create message windows with context
    3. Generate embeddings via OpenAI
    4. Store in ChromaDB
    5. Retrieve relevant context for new queries
    """
    print("\n" + "=" * 70)
    print("TEXT COMPATIBILITY - PIPELINE DEMONSTRATION")
    print("=" * 70)
    
    # Step 0: Check API key
    print("\n[STEP 0] Checking API Key...")
    check_api_key()
    
    # Step 1: Initialize components
    print("\n[STEP 1] Initializing Components...")
    print("-" * 50)
    
    embedder = OpenAIEmbedder()
    store = VectorStore("./data/chroma_db")
    pipeline = RAGPipeline(embedder, store)
    
    # Step 2: Parse messages
    print("\n[STEP 2] Parsing Messages...")
    print("-" * 50)
    
    sample_data = create_extended_sample_data()
    
    # Parse for Alice (she is "me" in her version)
    alice_parser = JSONParser(my_user_id="alice")
    alice_messages = alice_parser.parse_data(sample_data)
    
    # Parse for Bob (he is "me" in his version)
    bob_parser = JSONParser(my_user_id="bob")
    bob_messages = bob_parser.parse_data(sample_data)
    
    print(f"  Total messages: {len(alice_messages)}")
    
    # Step 3: Create message windows
    print("\n[STEP 3] Creating Message Windows...")
    print("-" * 50)
    
    # Create windows for all messages
    all_windows = create_message_windows(alice_messages, window_size=2)
    
    # Filter to each user's messages
    alice_windows = [w.to_dict() for w in all_windows if w.is_from_me]
    
    # For Bob, we need to re-parse with Bob as "me"
    bob_windows_raw = create_message_windows(bob_messages, window_size=2)
    bob_windows = [w.to_dict() for w in bob_windows_raw if w.is_from_me]
    
    print(f"  Alice's message windows: {len(alice_windows)}")
    print(f"  Bob's message windows: {len(bob_windows)}")
    
    # Show example window
    print("\n  Example window (Alice's message with context):")
    if alice_windows:
        example = alice_windows[2]
        print(f"  ---")
        print(f"  Context:\n{example['context']}")
        print(f"  ---")
        print(f"  Her actual message: \"{example['message_text']}\"")
    
    # Step 4: Create embeddings and store
    print("\n[STEP 4] Creating Embeddings & Storing...")
    print("-" * 50)
    
    # Index Alice's messages
    pipeline.index_user_messages("alice", alice_windows, overwrite=True)
    
    # Index Bob's messages
    pipeline.index_user_messages("bob", bob_windows, overwrite=True)
    
    # Show stats
    print("\n  Collection Statistics:")
    print(f"    Alice: {store.get_collection_stats('alice')}")
    print(f"    Bob: {store.get_collection_stats('bob')}")
    
    # Step 5: Demonstrate retrieval
    print("\n[STEP 5] Testing Retrieval...")
    print("-" * 50)
    
    test_queries = [
        ("alice", "hey want to get food later?"),
        ("alice", "I'm having a bad day"),
        ("bob", "want to hang out this weekend?"),
        ("bob", "have you seen any good movies?"),
    ]
    
    for user_id, query in test_queries:
        print(f"\n  🔍 Finding similar contexts for {user_id.upper()}")
        print(f"     Query: \"{query}\"")
        print("     " + "-" * 40)
        
        contexts = pipeline.retrieve_context(user_id, query, top_k=3)
        
        for i, ctx in enumerate(contexts, 1):
            print(f"\n     Match {i} (similarity: {ctx['similarity']:.3f})")
            print(f"     Response: \"{ctx['response']}\"")
    
    # Step 6: Show how this would be used in generation
    print("\n" + "=" * 70)
    print("HOW TO USE THIS FOR RESPONSE GENERATION")
    print("=" * 70)
    
    print("""
When you want to simulate how Alice would respond to a new message:

1. Get the current conversation context:
   current_context = "Them: want to grab dinner tonight?"

2. Retrieve similar past situations:
   contexts = pipeline.retrieve_context("alice", current_context, top_k=5)

3. Format the contexts for your LLM prompt:
   formatted = pipeline.format_context_for_prompt(contexts)

4. Build a prompt like:
   '''
   You are simulating Alice's texting style.
   
   Here's how she's responded in similar situations:
   {formatted}
   
   Current conversation:
   Them: want to grab dinner tonight?
   
   How would Alice respond? Match her tone, emoji usage, and style.
   '''

5. Send to your LLM (GPT-4, Claude, etc.) and get a response!
""")
    
    print("=" * 70)
    print("PIPELINE COMPLETE!")
    print("=" * 70)
    print(f"\nYour vector database is saved at: ./data/chroma_db")
    print("You can re-run this script and it will use the existing data.")
    print("\nNext steps:")
    print("  1. Replace sample data with your real iMessage exports")
    print("  2. Add LLM generation (see the architecture doc)")
    print("  3. Build the conversation simulation and UI")


if __name__ == "__main__":
    run_pipeline()
