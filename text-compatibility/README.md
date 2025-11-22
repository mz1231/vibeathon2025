# Text Compatibility - Vector Embedding System

A RAG (Retrieval-Augmented Generation) system that learns texting styles from iMessage history and simulates realistic conversations.

## 🏗️ Architecture

```
┌────────────────────┐
│   Message Parser   │  ← Parses iMessage SQLite or JSON exports
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│  OpenAI Embeddings │  ← Converts text to 1536-dim vectors
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│     ChromaDB       │  ← Stores vectors for similarity search
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│   RAG Pipeline     │  ← Retrieves relevant context for generation
└────────────────────┘
```

## 🚀 Quick Start

### 1. Set Up Your Environment

```bash
# Clone/navigate to the project
cd text-compatibility

# Install dependencies
pip install -r requirements.txt
```

### 2. Set Your OpenAI API Key

**Important:** Never put your API key directly in code!

```bash
# In your terminal (temporary - lasts until terminal closes)
export OPENAI_API_KEY="sk-your-key-here"

# OR add to your shell profile (permanent)
echo 'export OPENAI_API_KEY="sk-your-key-here"' >> ~/.zshrc
source ~/.zshrc
```

### 3. Run the Demo

```bash
python main.py
```

This will:
1. Create sample conversation data
2. Generate embeddings for each user
3. Store them in a local ChromaDB database
4. Demonstrate similarity search

## 📁 Project Structure

```
text-compatibility/
├── main.py                 # Main pipeline demonstration
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── src/
│   ├── __init__.py        # Module exports
│   ├── message_parser.py  # Parse iMessage/JSON data
│   ├── embeddings.py      # OpenAI embedding creation
│   └── vector_store.py    # ChromaDB storage & retrieval
└── data/
    └── chroma_db/         # Vector database (created on first run)
```

## 🔧 Component Details

### Message Parser (`src/message_parser.py`)

Handles two data sources:

**iMessage SQLite** (macOS):
```python
from src import IMessageParser

parser = IMessageParser()  # Uses default ~/Library/Messages/chat.db
conversations = parser.list_conversations()
messages = parser.parse_conversation("+15551234567")
```

**JSON Export**:
```python
from src import JSONParser

parser = JSONParser(my_user_id="alice")
messages = parser.parse_file("my_messages.json")
```

**Message Windows**:
```python
from src import create_message_windows

# Creates context around each message
windows = create_message_windows(messages, window_size=2)
```

### Embeddings (`src/embeddings.py`)

```python
from src import OpenAIEmbedder

embedder = OpenAIEmbedder()  # Reads API key from environment

# Single text
result = embedder.embed("Hello world")
print(len(result.embedding))  # 1536

# Batch (more efficient)
results = embedder.embed_batch(["Hello", "World", "!"])
```

### Vector Store (`src/vector_store.py`)

```python
from src import VectorStore, RAGPipeline

# Initialize
store = VectorStore("./data/chroma_db")
pipeline = RAGPipeline(embedder, store)

# Index a user's messages
pipeline.index_user_messages("alice", message_windows)

# Retrieve similar contexts
contexts = pipeline.retrieve_context("alice", "want to get dinner?")
```

## 🧠 How RAG Works

1. **Index Phase** (done once per user):
   - Parse all their messages
   - Create context windows around each message
   - Generate embeddings for each window
   - Store in ChromaDB

2. **Retrieval Phase** (done for each generation):
   - Embed the current conversation
   - Search for similar past contexts
   - Return the most relevant examples

3. **Generation Phase** (next step to implement):
   - Build a prompt with retrieved examples
   - Send to LLM (GPT-4, Claude, etc.)
   - Get a response that matches the user's style

## 📊 Example Output

```
🔍 Query: "want to get dinner?"

Match 1 (similarity: 0.892)
  Context: 
    Them: want to grab dinner? I'm craving thai food
    Me: ooh yes! that sounds amazing actually
  Response: "ooh yes! that sounds amazing actually"

Match 2 (similarity: 0.847)
  Context:
    Me: I'm so hungry rn
    Them: same, want to get lunch?
    Me: yes please! chipotle?
  Response: "yes please! chipotle?"
```

## 🔐 Security Notes

- **API Key**: Always use environment variables, never hardcode
- **Message Data**: Stored locally in `./data/chroma_db`
- **Privacy**: Data never leaves your machine (except embedding API calls)
- **Encryption**: Consider encrypting the ChromaDB directory for sensitive data

## 💰 Cost Estimation

OpenAI `text-embedding-3-small` pricing: **$0.02 per 1M tokens**

| Messages | Est. Tokens | Est. Cost |
|----------|-------------|-----------|
| 1,000    | ~50,000     | $0.001    |
| 10,000   | ~500,000    | $0.01     |
| 100,000  | ~5,000,000  | $0.10     |

Very affordable for personal use!

## 🛣️ Next Steps

1. **Add LLM Generation**: Use retrieved contexts to generate responses
2. **Build Conversation Simulator**: Have two user bots chat with each other
3. **Implement Compatibility Scoring**: Measure style/topic alignment
4. **Create UI**: Build the replay interface with timeline slider

## 📚 Resources

- [OpenAI Embeddings Guide](https://platform.openai.com/docs/guides/embeddings)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [RAG Explained](https://www.pinecone.io/learn/retrieval-augmented-generation/)

---

Built for Princeton Claude Vibeathon 2025 🐯
