'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import Sidebar from '@/components/Sidebar'
import { Button } from '@/components/ui'
import { type Conversation } from '@/lib/mockData'

export default function GeneratingPage() {
  const router = useRouter()
  const [conversation, setConversation] = useState<Conversation | null>(null)
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
    if (!conversation || !isPlaying) return

    // When playing, wait 3 seconds then navigate to replay
    const timer = setTimeout(() => {
      router.push('/replay')
    }, 3000)

    return () => clearTimeout(timer)
  }, [conversation, isPlaying, router])

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

  return (
    <div className="flex h-screen bg-[var(--bg)]">
      <Sidebar />

      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="px-8 py-5 border-b border-[var(--border)] bg-[var(--surface)]">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-sm font-semibold text-[var(--text-primary)] mb-1">
                Conversation Simulator
              </h2>
              <div className="text-xs text-[var(--text-secondary)]">
                {conversation.profileA.name} × {conversation.profileB.name}
              </div>
            </div>

            <Button
              variant="primary"
              size="md"
              onClick={() => setIsPlaying(true)}
              disabled={isPlaying}
            >
              {isPlaying ? (
                <span className="flex items-center gap-2">
                  <motion.div
                    className="w-3 h-3 border-2 border-white border-t-transparent rounded-full"
                    animate={{ rotate: 360 }}
                    transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                  />
                  Analyzing...
                </span>
              ) : (
                '▶ Play Simulation'
              )}
            </Button>
          </div>
        </div>

        {/* Messages Display */}
        <div className="flex-1 overflow-y-auto px-8 py-6">
          <div className="max-w-2xl mx-auto space-y-3">
            {conversation.messages.map((message) => {
              const isProfileA = message.senderId === conversation.profileA.id
              const profile = isProfileA ? conversation.profileA : conversation.profileB

              return (
                <div
                  key={message.id}
                  className={`flex items-start gap-3 ${isProfileA ? 'justify-end' : 'justify-start'}`}
                >
                  {!isProfileA && (
                    <div
                      className="w-6 h-6 rounded-full flex items-center justify-center text-white flex-shrink-0 mt-0.5 text-xs font-medium"
                      style={{ backgroundColor: profile.color }}
                    >
                      {profile.name[0]}
                    </div>
                  )}

                  <div
                    className={`max-w-[70%] px-3.5 py-2.5 rounded-lg border ${
                      isProfileA
                        ? 'bg-[#F3F7FF] dark:bg-[#1a2332] border-[#e3edff] dark:border-[#2a3a52] text-[var(--text-primary)]'
                        : 'bg-[var(--surface)] border-[var(--border)] text-[var(--text-primary)]'
                    }`}
                  >
                    <p className="text-sm leading-relaxed">{message.text}</p>
                  </div>

                  {isProfileA && (
                    <div
                      className="w-6 h-6 rounded-full flex items-center justify-center text-white flex-shrink-0 mt-0.5 text-xs font-medium"
                      style={{ backgroundColor: profile.color }}
                    >
                      {profile.name[0]}
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        </div>
      </div>
    </div>
  )
}
