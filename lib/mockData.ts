export interface Profile {
  id: string
  name: string
  color: string
}

export interface Message {
  id: string
  senderId: string
  text: string
  timestamp: number
}

export interface Insight {
  id: string
  title: string
  score: number
  description: string
  details: string
}

export interface Conversation {
  id: string
  profileA: Profile
  profileB: Profile
  messages: Message[]
  insights: Insight[]
}

export const mockProfiles: Profile[] = [
  { id: '1', name: 'Alex', color: '#3b82f6' },
  { id: '2', name: 'Jordan', color: '#8b5cf6' },
  { id: '3', name: 'Sam', color: '#ec4899' },
  { id: '4', name: 'Riley', color: '#f59e0b' },
  { id: '5', name: 'Casey', color: '#10b981' },
  { id: '6', name: 'Morgan', color: '#06b6d4' },
  { id: '7', name: 'Taylor', color: '#ef4444' },
  { id: '8', name: 'Avery', color: '#6366f1' },
]

export const generateMockConversation = (
  profileA: Profile,
  profileB: Profile,
  starter?: string
): Conversation => {
  const messages: Message[] = [
    { id: 'm1', senderId: profileA.id, text: starter || 'Hey! How have you been?', timestamp: 1 },
    { id: 'm2', senderId: profileB.id, text: "Pretty good! Just finished a project I've been working on", timestamp: 2 },
    { id: 'm3', senderId: profileA.id, text: 'Nice! What kind of project?', timestamp: 3 },
    { id: 'm4', senderId: profileB.id, text: "A web app for tracking habits. It's been challenging but fun!", timestamp: 4 },
    { id: 'm5', senderId: profileA.id, text: "That sounds awesome! I've been trying to build better habits myself", timestamp: 5 },
    { id: 'm6', senderId: profileB.id, text: "You should try it out when it's ready! I could use some beta testers 😊", timestamp: 6 },
    { id: 'm7', senderId: profileA.id, text: "Definitely! I'd love to. What tech stack are you using?", timestamp: 7 },
    { id: 'm8', senderId: profileB.id, text: 'Next.js and Tailwind mostly. Keeping it simple', timestamp: 8 },
    { id: 'm9', senderId: profileA.id, text: "Clean choice. I've been meaning to learn Next.js better", timestamp: 9 },
    { id: 'm10', senderId: profileB.id, text: "It's great once you get the hang of it. The routing is so intuitive", timestamp: 10 },
    { id: 'm11', senderId: profileA.id, text: 'Maybe we could work on something together sometime?', timestamp: 11 },
    { id: 'm12', senderId: profileB.id, text: "That would be amazing! I'm always down for a good collab", timestamp: 12 },
    { id: 'm13', senderId: profileA.id, text: "Perfect! Let's brainstorm some ideas this weekend", timestamp: 13 },
    { id: 'm14', senderId: profileB.id, text: 'Sounds like a plan. Coffee on Saturday?', timestamp: 14 },
    { id: 'm15', senderId: profileA.id, text: 'Saturday works! Around 2pm?', timestamp: 15 },
    { id: 'm16', senderId: profileB.id, text: 'Perfect, see you then! ☕', timestamp: 16 },
  ]

  const insights: Insight[] = [
    {
      id: 'i1',
      title: 'Overall Compatibility',
      score: 87,
      description: 'Strong connection with aligned interests',
      details: 'Your conversation flows naturally with shared enthusiasm for technology and collaboration. Both parties show genuine interest and engagement.',
    },
    {
      id: 'i2',
      title: 'Communication Style',
      score: 92,
      description: 'Very similar texting patterns',
      details: 'Message lengths are well-matched (avg 45 vs 48 characters). Both use casual tone with occasional emojis. Response enthusiasm is balanced.',
    },
    {
      id: 'i3',
      title: 'Conversation Flow',
      score: 85,
      description: 'Balanced back-and-forth rhythm',
      details: 'Response times are consistent. No one dominates the conversation. Natural progression from casual chat to making plans shows comfort.',
    },
    {
      id: 'i4',
      title: 'Topic Alignment',
      score: 88,
      description: 'Shared interests in tech and collaboration',
      details: 'Both engaged deeply in discussion about web development, habits, and future collaboration. No topic changes felt forced.',
    },
    {
      id: 'i5',
      title: 'Emotional Tone',
      score: 83,
      description: 'Positive and enthusiastic energy',
      details: 'Sentiment analysis shows consistently positive vibes. Both express excitement about shared activities. Emojis used appropriately to enhance warmth.',
    },
  ]

  return {
    id: `conv-${profileA.id}-${profileB.id}`,
    profileA,
    profileB,
    messages,
    insights,
  }
}

// Calculate insights based on message progress
export const calculateProgressiveInsights = (
  conversation: Conversation,
  progress: number // 0 to 1
): Insight[] => {
  const visibleMessages = Math.floor(conversation.messages.length * progress)

  return conversation.insights.map(insight => {
    const progressFactor = Math.min(1, visibleMessages / conversation.messages.length)
    const randomVariation = Math.random() * 10 - 5 // ±5 variation

    return {
      ...insight,
      score: Math.round(Math.max(0, Math.min(100, insight.score * progressFactor + randomVariation))),
    }
  })
}
