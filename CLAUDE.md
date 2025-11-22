# Text Compatibility App - Architecture & Implementation Guide

## Overview
An app that analyzes iMessage conversations to simulate chat interactions and measure compatibility between users. The system learns from uploaded message history to create chatbots that mimic user communication styles, then simulates conversations to generate compatibility scores.

---

## System Architecture

```
┌─────────────────┐      ┌──────────────┐      ┌─────────────────┐
│  Text Upload    │─────▶│   Database   │◀─────│  ML Model/RAG   │
│  Interface      │      │   (JSON)     │      │   System        │
└─────────────────┘      └──────────────┘      └─────────────────┘
                                │                       │
                                │                       │
                                ▼                       ▼
                         ┌──────────────────────────────┐
                         │   Conversation Simulator     │
                         └──────────────────────────────┘
                                        │
                                        ▼
                         ┌──────────────────────────────┐
                         │   Replay UI with Timeline    │
                         └──────────────────────────────┘
```

---

## Component Breakdown

### 1. Text Message Upload Interface

#### Functionality
- Extract iMessage conversations from user's device
- Parse message data (sender, timestamp, content, metadata)
- Upload to backend and store as JSON

#### Implementation Options

**Option A: macOS Desktop App (Recommended for iMessage)**
- **Technology**: Electron or Swift/SwiftUI
- **Access Method**: Read from `~/Library/Messages/chat.db` (SQLite database)
- **Requirements**: User permission for Full Disk Access
- **Pros**: Direct access to iMessage database, most reliable
- **Cons**: Requires macOS, needs system permissions

**Option B: Manual Export**
- **Technology**: Web interface with file upload
- **Process**: User exports messages manually (via third-party tools or scripts)
- **Format**: Accept JSON/CSV uploads
- **Pros**: Cross-platform, simpler implementation
- **Cons**: Extra step for users, less seamless

#### Data Schema
```json
{
  "conversation_id": "uuid",
  "participants": ["user_id_1", "user_id_2"],
  "messages": [
    {
      "id": "msg_uuid",
      "sender_id": "user_id_1",
      "text": "Message content",
      "timestamp": "2025-01-15T10:30:00Z",
      "metadata": {
        "reactions": [],
        "attachments": []
      }
    }
  ]
}
```

#### Implementation Steps
1. **macOS Access**: Create script to query SQLite database
   ```sql
   SELECT
     message.ROWID,
     message.text,
     message.date,
     handle.id as sender
   FROM message
   JOIN handle ON message.handle_id = handle.ROWID
   WHERE chat.chat_identifier = 'target_chat'
   ```

2. **Data Processing**:
   - Parse SQLite timestamps (macOS epoch starts 2001-01-01)
   - Clean message text, handle special characters
   - Associate messages with correct senders

3. **Upload API**:
   - POST endpoint `/api/upload-messages`
   - Validation and sanitization
   - Store in database

---

### 2. Model System

#### Approach: RAG (Retrieval-Augmented Generation)

**Why RAG over Fine-tuning?**
- Lower cost and complexity
- Works with less data per user
- Easier to update and iterate
- Can combine multiple conversation contexts

#### Architecture

```
User Query → Embedding → Vector Search → Relevant Messages → LLM + Context → Response
```

#### Components

**A. Embedding System**
- **Model**: OpenAI `text-embedding-3-small` or open-source alternative (e.g., `sentence-transformers`)
- **What to Embed**:
  - Individual messages with metadata
  - Message sequences (3-5 message windows for context)
  - Conversation topics/themes

**B. Vector Database**
- **Options**: Pinecone, Weaviate, Qdrant, or Supabase (with pgvector)
- **Storage**:
  - Message embeddings
  - User-specific indexes
  - Metadata for filtering (timestamp, sender, conversation_id)

**C. Retrieval Strategy**
```python
def get_relevant_context(user_id, current_conversation_state, k=10):
    """
    Retrieve k most relevant messages from user's history
    """
    # 1. Embed the recent conversation context
    query_embedding = embed(current_conversation_state)

    # 2. Search vector DB for similar past interactions
    results = vector_db.search(
        embedding=query_embedding,
        filter={"user_id": user_id},
        top_k=k
    )

    # 3. Return context for prompt
    return format_context(results)
```

**D. Response Generation**
- **Model**: GPT-4, Claude, or open-source (Llama, Mistral)
- **Prompt Structure**:
```
You are simulating [User A]'s texting style based on their message history.

Context from their past messages:
{retrieved_messages}

Current conversation:
{conversation_so_far}

How would [User A] respond? Match their tone, vocabulary, emoji usage, and message length.
```

#### Implementation Steps

1. **Preprocessing**:
   ```python
   # Extract features for each user
   - Average message length
   - Common phrases/words
   - Emoji patterns
   - Response time patterns
   - Conversation topics
   ```

2. **Create Embeddings**:
   ```python
   for message in user_messages:
       embedding = embedding_model.encode(message.text)
       vector_db.upsert({
           'id': message.id,
           'embedding': embedding,
           'metadata': {
               'user_id': message.sender,
               'timestamp': message.timestamp,
               'context': get_surrounding_messages(message)
           }
       })
   ```

3. **Generate Responses**:
   ```python
   def simulate_response(user_id, conversation_context):
       # Retrieve relevant past messages
       context = get_relevant_context(user_id, conversation_context)

       # Generate response with LLM
       prompt = build_prompt(context, conversation_context)
       response = llm.generate(prompt)

       return response
   ```

---

### 3. Message Replay Interface

#### Features
- Timeline slider for conversation progression
- Display both users' chatbots conversing
- Real-time compatibility score updates
- Message bubbles styled like iMessage
- Smooth animations as slider moves

#### UI Components

**A. Timeline Slider**
- **Technology**: React with `rc-slider` or custom HTML range input
- **Functionality**:
  - Scrub through conversation (0% to 100%)
  - Jump to specific message indices
  - Play/pause auto-progression

**B. Chat Display**
- **Layout**:
  - Left side: User A's messages (blue bubbles)
  - Right side: User B's messages (gray bubbles)
  - Timestamps between messages
- **Animation**: Fade in messages as slider progresses

**C. Compatibility Score**
- **Display**:
  - Large percentage at top (0-100%)
  - Color gradient (red → yellow → green)
  - Breakdown by categories (humor match, topic alignment, response style)
- **Updates**: Recalculate as slider moves

#### Compatibility Scoring Algorithm

```python
def calculate_compatibility(conversation_history):
    scores = {
        'response_time_sync': measure_timing_similarity(),
        'topic_alignment': measure_topic_overlap(),
        'sentiment_match': measure_sentiment_correlation(),
        'communication_style': measure_style_similarity(),
        'emoji_compatibility': measure_emoji_usage_match(),
        'engagement_level': measure_mutual_engagement()
    }

    # Weighted average
    weights = {
        'response_time_sync': 0.15,
        'topic_alignment': 0.25,
        'sentiment_match': 0.20,
        'communication_style': 0.20,
        'emoji_compatibility': 0.10,
        'engagement_level': 0.10
    }

    total_score = sum(scores[k] * weights[k] for k in scores)
    return {
        'overall': total_score,
        'breakdown': scores
    }
```

#### Implementation Steps

1. **Frontend Setup** (React + TailwindCSS):
   ```jsx
   function ReplayInterface({ conversationId }) {
     const [sliderValue, setSliderValue] = useState(0);
     const [messages, setMessages] = useState([]);
     const [compatibility, setCompatibility] = useState({});

     useEffect(() => {
       // Load conversation
       // Calculate which messages to show based on sliderValue
       const visibleMessages = allMessages.slice(0, sliderValue);
       setMessages(visibleMessages);

       // Recalculate compatibility
       const score = calculateCompatibility(visibleMessages);
       setCompatibility(score);
     }, [sliderValue]);

     return (
       <div className="replay-container">
         <CompatibilityScore score={compatibility} />
         <ChatBubbles messages={messages} />
         <TimelineSlider
           value={sliderValue}
           onChange={setSliderValue}
           max={allMessages.length}
         />
       </div>
     );
   }
   ```

2. **Backend API**:
   ```
   GET /api/conversations/:id/simulate
   - Generates full simulated conversation
   - Returns array of messages with metadata
   - Includes compatibility scores at each step
   ```

3. **Simulation Process**:
   ```python
   def simulate_conversation(user_a_id, user_b_id, num_exchanges=20):
       conversation = []

       for i in range(num_exchanges):
           # User A's turn
           context_a = build_context(conversation)
           response_a = simulate_response(user_a_id, context_a)
           conversation.append({
               'sender': 'user_a',
               'text': response_a,
               'timestamp': i * 2
           })

           # User B's turn
           context_b = build_context(conversation)
           response_b = simulate_response(user_b_id, context_b)
           conversation.append({
               'sender': 'user_b',
               'text': response_b,
               'timestamp': i * 2 + 1
           })

       return conversation
   ```

---

## Tech Stack Recommendations

### Frontend
- **Framework**: React + TypeScript
- **Styling**: TailwindCSS
- **State Management**: React Query + Zustand
- **Slider Component**: rc-slider or framer-motion
- **Charts**: Recharts (for compatibility breakdowns)

### Backend
- **API**: Node.js (Express) or Python (FastAPI)
- **Database**: PostgreSQL (with pgvector extension for embeddings)
- **Vector DB**: Pinecone (managed) or Qdrant (self-hosted)
- **LLM**: OpenAI API or Anthropic Claude API
- **Embeddings**: OpenAI text-embedding-3-small

### Infrastructure
- **Hosting**: Vercel (frontend) + Railway/Render (backend)
- **File Storage**: AWS S3 or Cloudflare R2 (for message exports)
- **Authentication**: Clerk or Auth0

---

## Implementation Roadmap

### Phase 1: MVP (Week 1-2)
1. Simple file upload interface (JSON/CSV)
2. Basic database schema for messages
3. Simple RAG pipeline with OpenAI
4. Static conversation display (no slider)

### Phase 2: Core Features (Week 3-4)
1. iMessage SQLite parser
2. Vector database integration
3. Improved prompt engineering for realistic responses
4. Timeline slider functionality
5. Basic compatibility scoring

### Phase 3: Polish (Week 5-6)
1. Beautiful UI with animations
2. Advanced compatibility metrics
3. Multiple conversation simulations
4. User profiles and history
5. Share functionality

---

## Database Schema

```sql
-- Users
CREATE TABLE users (
    id UUID PRIMARY KEY,
    name VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Conversations
CREATE TABLE conversations (
    id UUID PRIMARY KEY,
    user_a_id UUID REFERENCES users(id),
    user_b_id UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Messages (Original)
CREATE TABLE messages (
    id UUID PRIMARY KEY,
    conversation_id UUID REFERENCES conversations(id),
    sender_id UUID REFERENCES users(id),
    text TEXT,
    timestamp TIMESTAMP,
    metadata JSONB
);

-- Simulated Conversations
CREATE TABLE simulated_conversations (
    id UUID PRIMARY KEY,
    conversation_id UUID REFERENCES conversations(id),
    messages JSONB, -- Array of simulated messages
    compatibility_score JSONB, -- Overall and breakdown scores
    created_at TIMESTAMP DEFAULT NOW()
);

-- Vector embeddings (if using pgvector)
CREATE TABLE message_embeddings (
    id UUID PRIMARY KEY,
    message_id UUID REFERENCES messages(id),
    embedding vector(1536), -- Dimension depends on model
    user_id UUID REFERENCES users(id)
);

CREATE INDEX ON message_embeddings USING ivfflat (embedding vector_cosine_ops);
```

---

## Key Considerations

### Privacy & Security
- Encrypt message data at rest
- Never log actual message content in application logs
- Clear user consent for data usage
- Option to delete all data
- Anonymize data for model training

### Performance
- Pre-generate simulated conversations (don't do it in real-time)
- Cache embeddings
- Pagination for large conversations
- Lazy load messages in UI

### Accuracy
- Need sufficient message history (recommend 100+ messages minimum)
- Handle different conversation contexts (casual vs serious)
- Account for time gaps in conversations
- Consider external factors (user mood, time of day)

### Edge Cases
- Group chats (more than 2 participants)
- Media messages (photos, videos, audio)
- Deleted messages
- Read receipts and reactions

---

## Next Steps

1. **Choose your tech stack** based on team expertise
2. **Set up development environment** (databases, API keys)
3. **Build iMessage parser** or manual upload flow
4. **Implement basic RAG pipeline** with small dataset
5. **Create simple UI** to validate the concept
6. **Iterate on model quality** and compatibility scoring
7. **Polish UI/UX** with animations and timeline

---

## Resources

- **iMessage Database**: `~/Library/Messages/chat.db`
- **OpenAI Embeddings**: https://platform.openai.com/docs/guides/embeddings
- **RAG Tutorial**: https://www.pinecone.io/learn/retrieval-augmented-generation/
- **pgvector**: https://github.com/pgvector/pgvector
- **React Slider**: https://github.com/react-component/slider

---

## Questions to Resolve

1. Will this be desktop-only (macOS) or web-based with manual upload?
2. What's the target conversation length to simulate (10, 50, 100 messages)?
3. Should compatibility scores be based purely on style match or include content analysis?
4. Do you want to support group chats or just 1-on-1?
5. What's the budget for LLM API calls (affects model choice)?

---

Built for Princeton Claude Vibeathon 2025
