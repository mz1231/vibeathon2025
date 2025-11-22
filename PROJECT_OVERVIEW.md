# Vibe Check - Text Compatibility App

A clean, minimal web application for simulating conversations between AI personas and analyzing compatibility. Built for Princeton Claude Vibeathon 2025.

## 🎯 Current Implementation

### What's Built (MVP)

✅ **Landing Page** - Clean hero section with feature overview
✅ **Profile Grid** - 8 mock profiles in a landscape/grid layout
✅ **Profile Selection** - Click to select two profiles
✅ **Generation Modal** - Optional conversation starter input
✅ **Replay Interface** - Chat view with timeline slider
✅ **Insights Panel** - Scroll-based transitions through 5 metrics
✅ **Mock Data** - Complete conversation and compatibility scoring

### Live Demo

```bash
npm run dev
# Visit http://localhost:3000
```

## 🎨 Design System

### Fonts
- Primary: Helvetica Neue (clean, readable)
- Fallback: Helvetica, Arial, sans-serif
- Weight: Primarily `font-light` (300)

### Color Palette
- **Base**: White/Black (theme-aware)
- **Accents**: Profile-specific colors
- **Messages**: Blue (#3b82f6) for user, Gray for other
- **Borders**: Subtle gray-200/gray-800

### Design Philosophy
Inspired by:
- https://www.jesse-zhou.com/ - Minimal, spacious layouts
- https://ansubkhan.com/ - Smooth transitions, clean typography
- https://rauno.me/ - Scroll-based content reveals

## 📂 Project Structure

```
vibeathon2025/
├── app/
│   ├── layout.tsx          # Root layout with metadata
│   ├── page.tsx            # Landing page
│   ├── globals.css         # Global styles + Tailwind
│   ├── profiles/
│   │   └── page.tsx        # Profile grid & selection
│   └── replay/
│       └── page.tsx        # Conversation replay interface
├── components/
│   ├── ChatMessage.tsx     # Individual message bubbles
│   └── InsightsPanel.tsx   # Scroll-based insights display
├── lib/
│   └── mockData.ts         # Mock profiles, conversations, metrics
├── CLAUDE.md               # Full architecture documentation
└── PROJECT_OVERVIEW.md     # This file
```

## 🎬 User Flow

1. **Landing** (`/`)
   - Hero section with app description
   - "Explore Profiles" CTA button

2. **Profile Selection** (`/profiles`)
   - Grid of 8 profiles (rectangles with circular avatars)
   - Click two profiles to select
   - Modal appears to set conversation starter (optional)
   - "Generate" creates conversation

3. **Replay Interface** (`/replay`)
   - **Left**: Chat messages (iMessage-style bubbles)
   - **Right**: Insights panel (scroll-based)
   - **Bottom**: Timeline slider
   - Drag slider to scrub through conversation
   - Insights update dynamically based on progress

## 🔧 Key Features

### Timeline Slider
- Drag to control conversation progress (0-100%)
- Play/pause button for auto-progression
- Shows "X / Y messages" count
- Updates insights in real-time

### Insights Panel (Scroll-Based)
- 5 categories: Overall, Style, Flow, Topics, Tone
- Circular progress indicators
- Smooth snap-scroll transitions
- Dot navigation at top
- Score updates based on timeline position

### Compatibility Metrics
1. **Overall Compatibility** - Aggregate score
2. **Communication Style** - Message length, formality, emojis
3. **Conversation Flow** - Response rhythm, engagement
4. **Topic Alignment** - Interest overlap
5. **Emotional Tone** - Sentiment match, humor

## 🧪 Mock Data

Currently using 8 mock profiles with predefined colors:
- Alex, Jordan, Sam, Riley, Casey, Morgan, Taylor, Avery

Each conversation generates:
- 16 sample messages
- 5 insight categories with scores
- Dynamic score adjustments based on timeline progress

## 🚀 Next Steps (Future Development)

### Phase 1: Real Data Integration
- [ ] iMessage database parser (macOS)
- [ ] File upload system for manual imports
- [ ] User profile creation from real messages
- [ ] Database setup (PostgreSQL)

### Phase 2: AI Model Integration
- [ ] Set up vector database (Pinecone/Qdrant)
- [ ] Implement RAG pipeline
- [ ] Connect to LLM API (OpenAI/Claude)
- [ ] Generate realistic conversations

### Phase 3: Enhanced UX
- [ ] Animation polish (Framer Motion)
- [ ] Multiple conversation simulations
- [ ] Conversation export/sharing
- [ ] User authentication
- [ ] Dark mode toggle

### Phase 4: Advanced Features
- [ ] Group chat support (3+ people)
- [ ] Custom conversation scenarios
- [ ] Historical conversation analysis
- [ ] Compatibility trends over time

## 🛠️ Tech Stack

- **Framework**: Next.js 16 (App Router)
- **Language**: TypeScript
- **Styling**: TailwindCSS 4.1
- **Deployment**: Ready for Vercel

## 📖 Documentation

- **CLAUDE.md** - Complete technical architecture
  - iMessage upload strategies
  - RAG implementation guide
  - Database schemas
  - API design
  - Compatibility scoring algorithms

## 🎨 Component API

### `<ChatMessage />`
```tsx
<ChatMessage
  message={message}     // Message object
  profile={profile}     // Sender profile
  isUser={boolean}      // Styling variant
/>
```

### `<InsightsPanel />`
```tsx
<InsightsPanel
  insights={insights}   // Array of insight objects
/>
```

## 💡 Design Notes

1. **Minimal is Better**: No unnecessary decorations
2. **Typography First**: Let content breathe
3. **Smooth Transitions**: All state changes animated
4. **Responsive**: Works on mobile (though desktop-optimized)
5. **Accessibility**: Semantic HTML, keyboard nav supported

## 🐛 Known Limitations (MVP)

- Mock data only (no real conversations)
- Fixed conversation length (16 messages)
- No persistence (uses localStorage)
- Limited to 8 profiles
- No actual AI generation yet

## 📝 Code Style

- Component names: PascalCase
- Files: camelCase for utils, PascalCase for components
- Tailwind: Inline classes (no CSS modules)
- State: React hooks (useState, useEffect)
- Types: Explicit interfaces in mockData.ts

---

**Built with Claude Code for Princeton Vibeathon 2025**
