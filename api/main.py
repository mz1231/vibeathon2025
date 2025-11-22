#!/usr/bin/env python3
"""
FastAPI backend for the Text Compatibility App.
Provides endpoints for profile management and conversation simulation.
"""

import json
import os
import random
import sys
from datetime import datetime, timedelta
from typing import Optional
from pathlib import Path

from dotenv import load_dotenv

# Load .env file
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

# Add llm_usage to path for importing DualLLMSimulator
sys.path.insert(0, str(Path(__file__).parent.parent / "llm_usage"))
try:
    from dual_llm_simulator import DualLLMSimulator, load_user_messages_from_json
    DUAL_LLM_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import DualLLMSimulator: {e}")
    DUAL_LLM_AVAILABLE = False

app = FastAPI(title="Vibe Check API", version="1.0.0")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database directory for storing profiles and messages
DB_DIR = Path(__file__).parent.parent / "databases"
DB_DIR.mkdir(exist_ok=True)


# Pydantic models
class Profile(BaseModel):
    id: str
    name: str
    color: str
    bio: Optional[str] = None


class ProfileCreate(BaseModel):
    name: str
    bio: Optional[str] = None
    messages: Optional[list[str]] = None  # List of text messages for this profile


class SimulationRequest(BaseModel):
    profile_a_id: str
    profile_b_id: str
    num_messages: int = 20


class Message(BaseModel):
    id: str
    senderId: str
    text: str
    timestamp: int


class Insight(BaseModel):
    id: str
    title: str
    score: int
    description: str
    details: str


class ConversationResponse(BaseModel):
    id: str
    profileA: Profile
    profileB: Profile
    messages: list[Message]
    insights: list[Insight]


def load_profile_messages(profile_id: str) -> list[str]:
    """Load messages for a profile from the database."""
    messages_file = DB_DIR / f"{profile_id}_messages.json"
    if messages_file.exists():
        with open(messages_file, 'r', encoding='utf-8') as f:
            messages = json.load(f)
        # Filter out empty messages and system artifacts
        return [
            msg.strip() for msg in messages
            if msg and isinstance(msg, str)
            and not msg.startswith('&__kIM')
            and not msg.startswith('__kIM')
            and msg != '￼'
        ]
    return []


def save_profile_messages(profile_id: str, messages: list[str]):
    """Save messages for a profile to the database."""
    messages_file = DB_DIR / f"{profile_id}_messages.json"
    with open(messages_file, 'w', encoding='utf-8') as f:
        json.dump(messages, f, indent=2, ensure_ascii=False)


def get_profiles_db() -> dict:
    """Load all profiles from database."""
    profiles_file = DB_DIR / "profiles.json"
    if profiles_file.exists():
        with open(profiles_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_profiles_db(profiles: dict):
    """Save all profiles to database."""
    profiles_file = DB_DIR / "profiles.json"
    with open(profiles_file, 'w', encoding='utf-8') as f:
        json.dump(profiles, f, indent=2, ensure_ascii=False)


def create_persona_prompt(texts: list[str], person_name: str) -> str:
    """Create a prompt that captures the person's texting style."""
    sample_size = min(100, len(texts))
    sample_texts = random.sample(texts, sample_size) if len(texts) >= sample_size else texts

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


def generate_llm_response(client, persona_prompt: str, conversation_history: list, person_name: str) -> str:
    """Generate a response from the LLM based on the persona and conversation history."""
    messages = [{"role": "system", "content": persona_prompt}]

    # Add conversation history (last 10 messages for context)
    for msg in conversation_history[-10:]:
        if msg['sender'] == person_name:
            messages.append({"role": "assistant", "content": msg['text']})
        else:
            messages.append({"role": "user", "content": msg['text']})

    # If no history or last message was from this person, add a prompt to start
    if len(messages) == 1:
        messages.append({"role": "user", "content": "Hey what's up"})
    elif messages[-1]["role"] == "assistant":
        messages.append({"role": "user", "content": "Continue the conversation naturally with a short response."})

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=100,
            temperature=0.9,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error generating response: {e}")
        return "Hey what's up"


def calculate_compatibility_scores(messages: list[dict]) -> list[Insight]:
    """Calculate compatibility insights based on the conversation."""
    if len(messages) < 4:
        base_score = 50
    else:
        # Simple heuristics for demo
        avg_length_a = sum(len(m['text']) for m in messages[::2]) / max(1, len(messages) // 2)
        avg_length_b = sum(len(m['text']) for m in messages[1::2]) / max(1, len(messages) // 2)
        length_ratio = min(avg_length_a, avg_length_b) / max(avg_length_a, avg_length_b, 1)

        # Count emojis and question marks for engagement
        total_emojis = sum(1 for m in messages for c in m['text'] if ord(c) > 127)
        total_questions = sum(m['text'].count('?') for m in messages)

        base_score = int(60 + length_ratio * 20 + min(total_questions, 10) + min(total_emojis / 2, 5))
        base_score = min(95, max(50, base_score))

    return [
        Insight(
            id='i1',
            title='Overall Compatibility',
            score=base_score,
            description='Connection strength based on conversation analysis',
            details='Analyzing communication patterns, engagement levels, and conversational flow.',
        ),
        Insight(
            id='i2',
            title='Communication Style',
            score=min(100, base_score + random.randint(-5, 10)),
            description='Similarity in texting patterns',
            details='Message lengths, tone, and emoji usage are being compared.',
        ),
        Insight(
            id='i3',
            title='Conversation Flow',
            score=min(100, base_score + random.randint(-8, 8)),
            description='Back-and-forth rhythm analysis',
            details='Measuring response balance and natural progression.',
        ),
        Insight(
            id='i4',
            title='Topic Alignment',
            score=min(100, base_score + random.randint(-5, 5)),
            description='Shared interests and topics',
            details='Analyzing topic transitions and mutual engagement.',
        ),
        Insight(
            id='i5',
            title='Emotional Tone',
            score=min(100, base_score + random.randint(-3, 7)),
            description='Sentiment and energy match',
            details='Comparing emotional expressions and enthusiasm levels.',
        ),
    ]


@app.get("/")
def read_root():
    return {"message": "Vibe Check API is running"}


@app.get("/api/profiles")
def get_profiles():
    """Get all profiles."""
    profiles = get_profiles_db()
    return list(profiles.values())


@app.post("/api/profiles")
def create_profile(profile_data: ProfileCreate):
    """Create a new profile with message history."""
    profiles = get_profiles_db()

    profile_id = f"profile-{int(datetime.now().timestamp() * 1000)}"
    color = f"#{random.randint(0, 16777215):06x}"

    profile = {
        "id": profile_id,
        "name": profile_data.name,
        "color": color,
        "bio": profile_data.bio,
    }

    profiles[profile_id] = profile
    save_profiles_db(profiles)

    # Save messages if provided
    if profile_data.messages:
        save_profile_messages(profile_id, profile_data.messages)

    return profile


@app.get("/api/profiles/{profile_id}")
def get_profile(profile_id: str):
    """Get a specific profile."""
    profiles = get_profiles_db()
    if profile_id not in profiles:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profiles[profile_id]


@app.post("/api/profiles/{profile_id}/messages")
def upload_messages(profile_id: str, messages: list[str]):
    """Upload message history for a profile."""
    profiles = get_profiles_db()
    if profile_id not in profiles:
        raise HTTPException(status_code=404, detail="Profile not found")

    save_profile_messages(profile_id, messages)
    return {"message": f"Saved {len(messages)} messages for profile {profile_id}"}


@app.post("/api/simulate", response_model=ConversationResponse)
def simulate_conversation(request: SimulationRequest):
    """Simulate a conversation between two profiles using DualLLMSimulator with RAG."""
    profiles = get_profiles_db()

    if request.profile_a_id not in profiles:
        raise HTTPException(status_code=404, detail=f"Profile {request.profile_a_id} not found")
    if request.profile_b_id not in profiles:
        raise HTTPException(status_code=404, detail=f"Profile {request.profile_b_id} not found")

    profile_a = profiles[request.profile_a_id]
    profile_b = profiles[request.profile_b_id]

    # Load messages for each profile
    messages_a = load_profile_messages(request.profile_a_id)
    messages_b = load_profile_messages(request.profile_b_id)

    # Check if we have OpenAI API key and messages
    api_key = os.environ.get("OPENAI_API_KEY")
    use_dual_llm = DUAL_LLM_AVAILABLE and api_key and messages_a and messages_b

    if use_dual_llm:
        # Use DualLLMSimulator with RAG for better conversation generation
        simulator = DualLLMSimulator(llm_provider="openai")

        # Convert messages to context/response format for the simulator
        def convert_to_context_response(msgs):
            formatted = []
            for i in range(1, len(msgs)):
                formatted.append({
                    "context": f"Them: {msgs[i-1]}",
                    "response": msgs[i],
                    "timestamp": f"2025-01-{(i % 28) + 1:02d}T{(i % 24):02d}:00:00"
                })
            return formatted

        # Setup users in the simulator
        simulator.setup_user(profile_a['name'], convert_to_context_response(messages_a))
        simulator.setup_user(profile_b['name'], convert_to_context_response(messages_b))

        # Generate conversation using the simulator
        num_exchanges = request.num_messages // 2
        conversation_raw = simulator.simulate_conversation(
            user_a_id=profile_a['name'],
            user_b_id=profile_b['name'],
            starter_message="hey what's up?",
            num_exchanges=num_exchanges,
            temperature=0.9,
            verbose=False
        )

        # Convert to Message format
        messages = [
            Message(
                id=f"m{i+1}",
                senderId=profile_a['id'] if msg['sender'] == profile_a['name'] else profile_b['id'],
                text=msg['text'],
                timestamp=i+1
            )
            for i, msg in enumerate(conversation_raw)
        ]
    elif api_key and OpenAI and messages_a and messages_b:
        # Fallback to simple LLM generation without RAG
        client = OpenAI(api_key=api_key)
        persona_a = create_persona_prompt(messages_a, profile_a['name'])
        persona_b = create_persona_prompt(messages_b, profile_b['name'])

        conversation = []
        current_time = datetime.now() - timedelta(hours=2)
        current_speaker = random.choice([profile_a['name'], profile_b['name']])

        for i in range(request.num_messages):
            if current_speaker == profile_a['name']:
                prompt = persona_a
                sender_id = profile_a['id']
            else:
                prompt = persona_b
                sender_id = profile_b['id']

            text = generate_llm_response(client, prompt, conversation, current_speaker)

            message = {
                "id": f"m{i+1}",
                "sender": current_speaker,
                "senderId": sender_id,
                "text": text,
                "timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S")
            }
            conversation.append(message)

            time_delta = timedelta(seconds=random.randint(30, 300))
            current_time += time_delta
            current_speaker = profile_b['name'] if current_speaker == profile_a['name'] else profile_a['name']

        # Convert to Message format
        messages = [
            Message(
                id=msg['id'],
                senderId=msg['senderId'],
                text=msg['text'],
                timestamp=i+1
            )
            for i, msg in enumerate(conversation)
        ]
    else:
        # Fallback to simple mock conversation
        messages = generate_fallback_conversation(profile_a, profile_b, request.num_messages)

    # Calculate compatibility scores
    insights = calculate_compatibility_scores([{"text": m.text} for m in messages])

    return ConversationResponse(
        id=f"conv-{profile_a['id']}-{profile_b['id']}",
        profileA=Profile(**profile_a),
        profileB=Profile(**profile_b),
        messages=messages,
        insights=insights,
    )


def generate_fallback_conversation(profile_a: dict, profile_b: dict, num_messages: int) -> list[Message]:
    """Generate a simple fallback conversation when LLM is not available."""
    templates = [
        ("Hey! How's it going?", "Pretty good! Just finished up some work"),
        ("What are you up to?", "Not much, just relaxing. You?"),
        ("Nice! Any plans for the weekend?", "Maybe going to check out that new place downtown"),
        ("That sounds fun!", "Yeah should be good. You should come!"),
        ("I'd love to!", "Great, let's do it"),
        ("What time works for you?", "How about Saturday afternoon?"),
        ("Perfect!", "See you then!"),
        ("Looking forward to it", "Same here!"),
    ]

    messages = []
    for i in range(min(num_messages, len(templates) * 2)):
        template_idx = i // 2
        is_a_turn = i % 2 == 0

        if template_idx < len(templates):
            text = templates[template_idx][0 if is_a_turn else 1]
        else:
            text = "..."

        messages.append(Message(
            id=f"m{i+1}",
            senderId=profile_a['id'] if is_a_turn else profile_b['id'],
            text=text,
            timestamp=i+1
        ))

    return messages


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
