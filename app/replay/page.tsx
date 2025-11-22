'use client'

import React, { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import ChatMessage from '@/components/ChatMessage'
import Sidebar from '@/components/Sidebar'
import { type Conversation, calculateProgressiveInsights } from '@/lib/mockData'

export default function ReplayPage() {
  const router = useRouter()
  const [conversation, setConversation] = useState<Conversation | null>(null)
  const [progress, setProgress] = useState(1) // Start at 100% (1.0) to show all messages
  const [isPlaying, setIsPlaying] = useState(false)
  const [hasStartedSimulation, setHasStartedSimulation] = useState(false)
  const [typingUser, setTypingUser] = useState<string | null>(null)
  const chatContainerRef = React.useRef<HTMLDivElement>(null)

  useEffect(() => {
    const stored = localStorage.getItem('currentConversation')
    if (stored) {
      setConversation(JSON.parse(stored))
    } else {
      router.push('/profiles')
    }
  }, [router])

  const handleStartSimulation = () => {
    setProgress(0)
    setHasStartedSimulation(true)
    setIsPlaying(true)
  }

  useEffect(() => {
    if (!isPlaying || !conversation) return

    const totalMessages = conversation.messages.length
    const incrementPerMessage = 1 / totalMessages

    const interval = setInterval(() => {
      setProgress(prev => {
        const nextProgress = prev + incrementPerMessage

        if (nextProgress >= 1) {
          setIsPlaying(false)
          setTypingUser(null)
          return 1
        }

        // Show typing indicator for next message
        const nextMessageIndex = Math.floor(nextProgress * totalMessages)
        if (nextMessageIndex < totalMessages) {
          const nextMessage = conversation.messages[nextMessageIndex]
          setTypingUser(nextMessage.senderId)
        }

        return nextProgress
      })
    }, 1500) // 1.5 seconds per message

    return () => clearInterval(interval)
  }, [isPlaying, conversation])

  // Auto-scroll to bottom when new messages appear
  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTo({
        top: chatContainerRef.current.scrollHeight,
        behavior: 'smooth'
      })
    }
  }, [progress, typingUser])

  if (!conversation) {
    return (
      <div className="flex h-screen bg-[var(--bg)]">
        <Sidebar />
        <div className="flex-1 flex items-center justify-center">
          <div className="text-sm text-[var(--text-secondary)]">Loading...</div>
        </div>
      </div>
    )
  }

  const visibleMessageCount = Math.max(1, Math.floor(conversation.messages.length * progress))
  const visibleMessages = conversation.messages.slice(0, visibleMessageCount)
  const currentInsights = calculateProgressiveInsights(conversation, progress)
  const overallScore = currentInsights[0]?.score || 0

  return (
    <div className="flex h-screen bg-[var(--bg)]">
      {/* Sidebar */}
      <Sidebar />

      {/* Middle Panel - Score & Timeline */}
      <div className="w-[400px] bg-[var(--surface)] border-r border-[var(--border)] flex flex-col">
        {/* Header with profiles */}
        <div className="px-6 py-5 border-b border-[var(--border)]">
          <div className="flex items-center gap-3 mb-1">
            <div className="flex items-center gap-2 text-xs">
              <div
                className="w-5 h-5 rounded-full flex items-center justify-center text-white font-medium"
                style={{ backgroundColor: conversation.profileA.color, fontSize: '10px' }}
              >
                {conversation.profileA.name[0]}
              </div>
              <span className="text-[var(--text-primary)]">{conversation.profileA.name}</span>
            </div>

            <span className="text-[var(--text-secondary)]">×</span>

            <div className="flex items-center gap-2 text-xs">
              <div
                className="w-5 h-5 rounded-full flex items-center justify-center text-white font-medium"
                style={{ backgroundColor: conversation.profileB.color, fontSize: '10px' }}
              >
                {conversation.profileB.name[0]}
              </div>
              <span className="text-[var(--text-primary)]">{conversation.profileB.name}</span>
            </div>
          </div>
        </div>

        {/* Compatibility Score */}
        <div className="px-6 py-8 border-b border-[var(--border)]">
          <div className="bg-[var(--bg)] border border-[var(--border)] rounded-lg p-6 text-center">
            <div className="text-4xl font-semibold text-[var(--text-primary)] mb-2">
              {overallScore}%
            </div>
            <div className="text-sm text-[var(--text-primary)] font-medium mb-1">
              Compatibility Score
            </div>
            <div className="text-xs text-[var(--text-secondary)]">
              {overallScore >= 80 ? 'Strong conversational match' : overallScore >= 60 ? 'Good compatibility' : 'Moderate compatibility'}
            </div>
          </div>
        </div>

        {/* Timeline Simulation */}
        <div className="flex-1 px-6 py-6">
          <h3 className="text-xs font-semibold text-[var(--text-primary)] mb-4">
            TIMELINE SIMULATION
          </h3>

          {/* Timeline visualization */}
          <div className="mb-6">
            <div className="relative h-0.5 bg-[var(--border)] rounded-full">
              <div
                className="absolute top-0 left-0 h-full bg-[var(--accent)] rounded-full transition-all duration-200"
                style={{ width: `${progress * 100}%` }}
              />
              {conversation.messages.map((_, index) => {
                const position = (index / (conversation.messages.length - 1)) * 100
                const isPast = index < visibleMessageCount

                return (
                  <div
                    key={index}
                    className={`absolute top-1/2 -translate-y-1/2 w-2 h-2 rounded-full transition-colors ${
                      isPast ? 'bg-[var(--accent)]' : 'bg-[var(--border)]'
                    }`}
                    style={{ left: `${position}%` }}
                  />
                )
              })}
            </div>
          </div>

          {/* Controls */}
          <div className="space-y-4">
            {!hasStartedSimulation ? (
              <button
                onClick={handleStartSimulation}
                className="w-full px-4 py-2.5 bg-[var(--accent)] hover:bg-[var(--accent-hover)] text-white rounded-lg text-sm font-medium transition-colors"
              >
                ▶ Start Simulation
              </button>
            ) : (
              <div className="flex items-center gap-3">
                <button
                  onClick={() => setIsPlaying(!isPlaying)}
                  className="w-8 h-8 border border-[var(--border)] rounded flex items-center justify-center hover:border-[var(--accent)] transition-colors"
                >
                  {isPlaying ? (
                    <svg width="10" height="12" viewBox="0 0 12 14" fill="none" className="text-[var(--text-primary)]">
                      <rect width="4" height="14" fill="currentColor" />
                      <rect x="8" width="4" height="14" fill="currentColor" />
                    </svg>
                  ) : (
                    <svg width="10" height="12" viewBox="0 0 12 14" fill="none" className="text-[var(--text-primary)] ml-0.5">
                      <path d="M12 7L0 14V0L12 7Z" fill="currentColor" />
                    </svg>
                  )}
                </button>

                <div className="flex-1">
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={progress * 100}
                    onChange={(e) => setProgress(Number(e.target.value) / 100)}
                    className="w-full h-0.5 bg-[var(--border)] appearance-none cursor-pointer slider rounded-full"
                  />
                </div>
              </div>
            )}

            <div className="text-xs text-[var(--text-secondary)]">
              {visibleMessageCount} / {conversation.messages.length} messages
            </div>
          </div>

          {/* Insights breakdown */}
          <div className="mt-8 space-y-3">
            <h3 className="text-xs font-semibold text-[var(--text-primary)]">
              ANALYSIS BREAKDOWN
            </h3>
            {currentInsights.slice(0, 3).map((insight) => (
              <div key={insight.id} className="flex items-center justify-between text-xs">
                <span className="text-[var(--text-secondary)]">{insight.title}</span>
                <span className="text-[var(--text-primary)] font-medium">{insight.score}%</span>
              </div>
            ))}
          </div>
        </div>

        <style jsx>{`
          .slider::-webkit-slider-thumb {
            appearance: none;
            width: 14px;
            height: 14px;
            background: var(--accent);
            cursor: pointer;
            border-radius: 50%;
          }

          .slider::-moz-range-thumb {
            width: 14px;
            height: 14px;
            background: var(--accent);
            cursor: pointer;
            border-radius: 50%;
            border: none;
          }

          .slider:hover::-webkit-slider-thumb {
            background: var(--accent-hover);
          }

          .slider:hover::-moz-range-thumb {
            background: var(--accent-hover);
          }
        `}</style>
      </div>

      {/* Right Panel - Chat Transcript */}
      <div className="flex-1 flex flex-col bg-[var(--bg)]">
        {/* Header */}
        <div className="px-8 py-5 border-b border-[var(--border)] bg-[var(--surface)]">
          <h2 className="text-sm font-semibold text-[var(--text-primary)]">
            Chat Transcript
          </h2>
        </div>

        {/* Messages */}
        <div ref={chatContainerRef} className="flex-1 overflow-y-auto px-8 py-6">
          <div className="max-w-2xl">
            {visibleMessages.map((message) => (
              <ChatMessage
                key={message.id}
                message={message}
                profile={
                  message.senderId === conversation.profileA.id
                    ? conversation.profileA
                    : conversation.profileB
                }
                isUser={message.senderId === conversation.profileA.id}
              />
            ))}

            {/* Typing Indicator */}
            {typingUser && (
              <div className={`flex items-start gap-2.5 mb-4 animate-fadeIn ${typingUser === conversation.profileA.id ? 'justify-end' : 'justify-start'}`}>
                {typingUser !== conversation.profileA.id && (
                  <div
                    className="w-6 h-6 rounded-full flex items-center justify-center text-white flex-shrink-0 mt-0.5 font-medium"
                    style={{ backgroundColor: conversation.profileB.color, fontSize: '11px' }}
                  >
                    {conversation.profileB.name[0]}
                  </div>
                )}

                <div className={`px-3.5 py-2.5 rounded-lg border ${
                  typingUser === conversation.profileA.id
                    ? 'bg-[#F3F7FF] dark:bg-[#1a2332] border-[#e3edff] dark:border-[#2a3a52]'
                    : 'bg-[var(--surface)] border-[var(--border)]'
                }`}>
                  <div className="flex gap-1.5 items-center">
                    <div className="w-1.5 h-1.5 rounded-full bg-[var(--text-secondary)] animate-bounce" style={{ animationDelay: '0ms' }} />
                    <div className="w-1.5 h-1.5 rounded-full bg-[var(--text-secondary)] animate-bounce" style={{ animationDelay: '150ms' }} />
                    <div className="w-1.5 h-1.5 rounded-full bg-[var(--text-secondary)] animate-bounce" style={{ animationDelay: '300ms' }} />
                  </div>
                </div>

                {typingUser === conversation.profileA.id && (
                  <div
                    className="w-6 h-6 rounded-full flex items-center justify-center text-white flex-shrink-0 mt-0.5 font-medium"
                    style={{ backgroundColor: conversation.profileA.color, fontSize: '11px' }}
                  >
                    {conversation.profileA.name[0]}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
