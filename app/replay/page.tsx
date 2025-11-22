'use client'

import React, { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import ChatMessage from '@/components/ChatMessage'
import InsightsPanel from '@/components/InsightsPanel'
import { type Conversation, calculateProgressiveInsights } from '@/lib/mockData'

export default function ReplayPage() {
  const router = useRouter()
  const [conversation, setConversation] = useState<Conversation | null>(null)
  const [progress, setProgress] = useState(0) // Start at 0
  const [isPlaying, setIsPlaying] = useState(false)
  const [typingUser, setTypingUser] = useState<string | null>(null)
  const chatContainerRef = React.useRef<HTMLDivElement>(null)

  useEffect(() => {
    const stored = localStorage.getItem('currentConversation')
    if (stored) {
      setConversation(JSON.parse(stored))
      // Auto-start playing when loaded
      setTimeout(() => setIsPlaying(true), 500)
    } else {
      router.push('/profiles')
    }
  }, [router])

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
      <div className="min-h-screen bg-white dark:bg-black flex items-center justify-center">
        <div className="text-xl font-light">Loading...</div>
      </div>
    )
  }

  const visibleMessageCount = Math.max(1, Math.floor(conversation.messages.length * progress))
  const visibleMessages = conversation.messages.slice(0, visibleMessageCount)
  const currentInsights = calculateProgressiveInsights(conversation, progress)

  return (
    <main className="h-screen bg-white dark:bg-black flex flex-col">
      {/* Header */}
      <div className="border-b border-gray-200 dark:border-gray-800 px-8 py-3">
        <div className="flex items-center justify-between max-w-[1600px] mx-auto">
          <button
            onClick={() => router.push('/profiles')}
            className="text-xs tracking-tight hover:opacity-60 transition-opacity"
          >
            ← Back
          </button>

          <div className="flex items-center gap-3 text-xs tracking-tight">
            <div className="flex items-center gap-1.5">
              <div
                className="w-4 h-4 rounded-full flex items-center justify-center text-white"
                style={{ backgroundColor: conversation.profileA.color, fontSize: '8px' }}
              >
                {conversation.profileA.name[0]}
              </div>
              <span>{conversation.profileA.name}</span>
            </div>

            <span className="text-gray-400">×</span>

            <div className="flex items-center gap-1.5">
              <div
                className="w-4 h-4 rounded-full flex items-center justify-center text-white"
                style={{ backgroundColor: conversation.profileB.color, fontSize: '8px' }}
              >
                {conversation.profileB.name[0]}
              </div>
              <span>{conversation.profileB.name}</span>
            </div>
          </div>

          <div className="w-16" />
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Chat Area */}
        <div ref={chatContainerRef} className="flex-1 overflow-y-auto px-6 py-8 scroll-smooth dotted-background">
          <div className="max-w-3xl mx-auto space-y-4 py-4">
            {visibleMessages.map((message, index) => (
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
              <div className={`flex items-start gap-3 ${typingUser === conversation.profileA.id ? 'justify-end' : 'justify-start'} animate-fadeIn`}>
                {typingUser !== conversation.profileA.id && (
                  <div
                    className="w-8 h-8 rounded-full flex items-center justify-center text-white flex-shrink-0 text-sm font-medium"
                    style={{ backgroundColor: conversation.profileB.color }}
                  >
                    {conversation.profileB.name[0]}
                  </div>
                )}

                <div className={`px-5 py-3 rounded-3xl ${
                  typingUser === conversation.profileA.id
                    ? 'bg-blue-500 shadow-sm'
                    : 'bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 shadow-sm'
                }`}>
                  <div className="flex gap-1.5 items-center">
                    <div className="w-2 h-2 rounded-full bg-gray-400 dark:bg-gray-500 animate-bounce" style={{ animationDelay: '0ms' }} />
                    <div className="w-2 h-2 rounded-full bg-gray-400 dark:bg-gray-500 animate-bounce" style={{ animationDelay: '150ms' }} />
                    <div className="w-2 h-2 rounded-full bg-gray-400 dark:bg-gray-500 animate-bounce" style={{ animationDelay: '300ms' }} />
                  </div>
                </div>

                {typingUser === conversation.profileA.id && (
                  <div
                    className="w-8 h-8 rounded-full flex items-center justify-center text-white flex-shrink-0 text-sm font-medium"
                    style={{ backgroundColor: conversation.profileA.color }}
                  >
                    {conversation.profileA.name[0]}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Insights Panel */}
        <div className="w-[380px] border-l border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-950">
          <div className="h-full py-8">
            <h2 className="text-base font-semibold text-center mb-8 px-6">Insights</h2>
            <InsightsPanel insights={currentInsights} />
          </div>
        </div>
      </div>

      {/* Timeline Slider */}
      <div className="border-t border-gray-200 dark:border-gray-800 px-6 py-5 bg-white dark:bg-black">
        <div className="max-w-[1600px] mx-auto">
          <div className="flex items-center gap-6">
            {/* Play/Pause Button */}
            <button
              onClick={() => setIsPlaying(!isPlaying)}
              className="w-10 h-10 rounded-lg border border-gray-200 dark:border-gray-800 flex items-center justify-center hover:bg-gray-50 dark:hover:bg-gray-900 transition-colors flex-shrink-0"
            >
              {isPlaying ? (
                <svg
                  width="12"
                  height="14"
                  viewBox="0 0 12 14"
                  fill="none"
                  className="text-black dark:text-white"
                >
                  <rect width="4" height="14" fill="currentColor" />
                  <rect x="8" width="4" height="14" fill="currentColor" />
                </svg>
              ) : (
                <svg
                  width="12"
                  height="14"
                  viewBox="0 0 12 14"
                  fill="none"
                  className="text-black dark:text-white ml-0.5"
                >
                  <path d="M12 7L0 14V0L12 7Z" fill="currentColor" />
                </svg>
              )}
            </button>

            {/* Progress Info */}
            <div className="text-sm text-gray-500 dark:text-gray-500 w-28 flex-shrink-0">
              {visibleMessageCount} / {conversation.messages.length}
            </div>

            {/* Slider */}
            <div className="flex-1 relative">
              <input
                type="range"
                min="0"
                max="100"
                value={progress * 100}
                onChange={(e) => setProgress(Number(e.target.value) / 100)}
                className="w-full h-1 bg-gray-200 dark:bg-gray-800 appearance-none cursor-pointer slider rounded-full"
              />
            </div>

            {/* Overall Score */}
            <div className="text-right w-24 flex-shrink-0">
              <div className="text-2xl font-semibold">{currentInsights[0]?.score || 0}%</div>
              <div className="text-xs text-gray-500 dark:text-gray-500">
                Compatibility
              </div>
            </div>
          </div>
        </div>
      </div>

      <style jsx>{`
        .slider::-webkit-slider-thumb {
          appearance: none;
          width: 16px;
          height: 16px;
          background: black;
          cursor: pointer;
          border-radius: 0;
        }

        .slider::-moz-range-thumb {
          width: 16px;
          height: 16px;
          background: black;
          cursor: pointer;
          border-radius: 0;
          border: none;
        }

        @media (prefers-color-scheme: dark) {
          .slider::-webkit-slider-thumb {
            background: white;
          }

          .slider::-moz-range-thumb {
            background: white;
          }
        }
      `}</style>
    </main>
  )
}
