'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import ChatMessage from '@/components/ChatMessage'
import InsightsPanel from '@/components/InsightsPanel'
import { type Conversation, calculateProgressiveInsights } from '@/lib/mockData'

export default function ReplayPage() {
  const router = useRouter()
  const [conversation, setConversation] = useState<Conversation | null>(null)
  const [progress, setProgress] = useState(1) // 0 to 1
  const [isPlaying, setIsPlaying] = useState(false)

  useEffect(() => {
    const stored = localStorage.getItem('currentConversation')
    if (stored) {
      setConversation(JSON.parse(stored))
    } else {
      router.push('/profiles')
    }
  }, [router])

  useEffect(() => {
    if (!isPlaying) return

    const interval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 1) {
          setIsPlaying(false)
          return 1
        }
        return Math.min(1, prev + 0.02)
      })
    }, 200)

    return () => clearInterval(interval)
  }, [isPlaying])

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
        <div className="flex-1 overflow-y-auto px-8 py-6">
          <div className="max-w-2xl mx-auto">
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
          </div>
        </div>

        {/* Insights Panel */}
        <div className="w-[320px] border-l border-gray-200 dark:border-gray-800">
          <div className="h-full py-6">
            <h2 className="text-sm font-medium text-center mb-6 px-6 tracking-tight">Insights</h2>
            <InsightsPanel insights={currentInsights} />
          </div>
        </div>
      </div>

      {/* Timeline Slider */}
      <div className="border-t border-gray-200 dark:border-gray-800 px-8 py-4 bg-white dark:bg-black">
        <div className="max-w-[1600px] mx-auto">
          <div className="flex items-center gap-4">
            {/* Play/Pause Button */}
            <button
              onClick={() => setIsPlaying(!isPlaying)}
              className="w-8 h-8 border border-gray-200 dark:border-gray-800 flex items-center justify-center hover:opacity-60 transition-opacity flex-shrink-0"
            >
              {isPlaying ? (
                <svg
                  width="10"
                  height="12"
                  viewBox="0 0 12 14"
                  fill="none"
                  className="text-black dark:text-white"
                >
                  <rect width="4" height="14" fill="currentColor" />
                  <rect x="8" width="4" height="14" fill="currentColor" />
                </svg>
              ) : (
                <svg
                  width="10"
                  height="12"
                  viewBox="0 0 12 14"
                  fill="none"
                  className="text-black dark:text-white ml-0.5"
                >
                  <path d="M12 7L0 14V0L12 7Z" fill="currentColor" />
                </svg>
              )}
            </button>

            {/* Progress Info */}
            <div className="text-xs text-gray-500 dark:text-gray-500 w-24 flex-shrink-0 tracking-tight">
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
                className="w-full h-px bg-gray-200 dark:bg-gray-800 appearance-none cursor-pointer slider"
              />
            </div>

            {/* Overall Score */}
            <div className="text-right w-20 flex-shrink-0">
              <div className="text-lg font-medium tracking-tight">{currentInsights[0]?.score || 0}%</div>
              <div className="text-xs text-gray-500 dark:text-gray-500 tracking-tight">
                Score
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
