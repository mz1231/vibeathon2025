'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { mockProfiles, generateMockConversation, type Profile } from '@/lib/mockData'

export default function ProfilesPage() {
  const router = useRouter()
  const [selectedProfiles, setSelectedProfiles] = useState<Profile[]>([])
  const [showModal, setShowModal] = useState(false)
  const [conversationStarter, setConversationStarter] = useState('')

  const handleProfileClick = (profile: Profile) => {
    if (selectedProfiles.find(p => p.id === profile.id)) {
      setSelectedProfiles(selectedProfiles.filter(p => p.id !== profile.id))
    } else if (selectedProfiles.length < 2) {
      const newSelection = [...selectedProfiles, profile]
      setSelectedProfiles(newSelection)

      if (newSelection.length === 2) {
        setShowModal(true)
      }
    }
  }

  const handleGenerate = () => {
    if (selectedProfiles.length === 2) {
      const conversation = generateMockConversation(
        selectedProfiles[0],
        selectedProfiles[1],
        conversationStarter || undefined
      )
      localStorage.setItem('currentConversation', JSON.stringify(conversation))
      router.push('/replay')
    }
  }

  const handleCancel = () => {
    setShowModal(false)
    setSelectedProfiles([])
    setConversationStarter('')
  }

  return (
    <main className="min-h-screen bg-white dark:bg-black">
      <div className="max-w-5xl mx-auto px-6 py-20">
        {/* Header */}
        <div className="mb-16">
          <h1 className="text-4xl font-semibold tracking-tight mb-4">Select Profiles</h1>
          <p className="text-base text-gray-500 dark:text-gray-400">
            Choose two profiles to simulate a conversation
          </p>
        </div>

        {/* Selection Indicator */}
        {selectedProfiles.length > 0 && (
          <div className="mb-12 pb-6 border-b border-gray-200 dark:border-gray-800">
            <div className="text-sm text-gray-500 dark:text-gray-400 mb-4">Selected profiles</div>
            <div className="flex gap-4">
              {selectedProfiles.map(profile => (
                <div
                  key={profile.id}
                  className="flex items-center gap-3"
                >
                  <div
                    className="w-10 h-10 rounded-full flex items-center justify-center text-white text-sm"
                    style={{ backgroundColor: profile.color }}
                  >
                    {profile.name[0]}
                  </div>
                  <span className="text-sm font-medium">{profile.name}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Profile Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
          {mockProfiles.map((profile, index) => {
            const isSelected = selectedProfiles.find(p => p.id === profile.id)
            const isDisabled = selectedProfiles.length === 2 && !isSelected

            return (
              <button
                key={profile.id}
                onClick={() => handleProfileClick(profile)}
                disabled={isDisabled}
                style={{ animationDelay: `${index * 50}ms` }}
                className={`
                  group text-left animate-fadeIn
                  ${isDisabled ? 'opacity-40 cursor-not-allowed' : 'cursor-pointer'}
                `}
              >
                {/* Card Container */}
                <div
                  className={`
                    relative bg-white dark:bg-gray-900 border overflow-hidden
                    transition-all duration-300
                    ${isSelected
                      ? 'border-black dark:border-white shadow-xl'
                      : 'border-gray-200 dark:border-gray-800 group-hover:shadow-lg'
                    }
                  `}
                >
                  {/* Image Area - with colored background and avatar */}
                  <div
                    className="aspect-[4/3] flex items-center justify-center relative"
                    style={{ backgroundColor: `${profile.color}20` }}
                  >
                    <div
                      className="w-20 h-20 rounded-full flex items-center justify-center text-white text-2xl font-semibold shadow-lg"
                      style={{ backgroundColor: profile.color }}
                    >
                      {profile.name[0]}
                    </div>

                    {/* Selection Checkmark */}
                    {isSelected && (
                      <div className="absolute top-3 right-3 w-6 h-6 rounded-full bg-black dark:bg-white flex items-center justify-center animate-scaleIn">
                        <svg width="12" height="10" viewBox="0 0 12 10" fill="none">
                          <path d="M1 5L4.5 8.5L11 1.5" stroke="white" className="dark:stroke-black" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                        </svg>
                      </div>
                    )}
                  </div>

                  {/* Content Area */}
                  <div className="p-4">
                    <h3 className="font-semibold text-sm mb-1 uppercase tracking-wide">
                      {profile.name}
                    </h3>
                    <p className="text-xs text-gray-600 dark:text-gray-400">
                      AI Profile {index + 1}
                    </p>
                  </div>

                  {/* Info Icon (bottom right like adamhartwig) */}
                  <div className="absolute bottom-3 right-3 w-5 h-5 rounded-full border border-gray-300 dark:border-gray-700 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                    <svg width="10" height="10" viewBox="0 0 10 10" fill="none">
                      <circle cx="5" cy="3" r="0.5" fill="currentColor"/>
                      <path d="M5 5v3" stroke="currentColor" strokeWidth="0.8" strokeLinecap="round"/>
                    </svg>
                  </div>
                </div>
              </button>
            )
          })}
        </div>
      </div>

      {/* Generation Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/50 dark:bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 px-6 animate-fadeIn">
          <div className="bg-white dark:bg-black border border-gray-200 dark:border-gray-800 max-w-md w-full p-8 shadow-2xl animate-scaleIn">
            <h2 className="text-xl font-semibold tracking-tight mb-8">Generate Conversation</h2>

            <div className="mb-8">
              <p className="text-xs text-gray-500 dark:text-gray-400 mb-4 tracking-tight uppercase">
                Selected profiles
              </p>
              <div className="flex gap-4">
                {selectedProfiles.map(profile => (
                  <div key={profile.id} className="flex items-center gap-3 text-sm">
                    <div
                      className="w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-medium shadow-sm"
                      style={{ backgroundColor: profile.color }}
                    >
                      {profile.name[0]}
                    </div>
                    <span className="font-medium tracking-tight">{profile.name}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="mb-8">
              <label className="block text-xs text-gray-500 dark:text-gray-400 mb-3 tracking-tight uppercase font-medium">
                Conversation Starter (Optional)
              </label>
              <input
                type="text"
                autoFocus
                value={conversationStarter}
                onChange={(e) => setConversationStarter(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    handleGenerate()
                  }
                }}
                placeholder="e.g., Hey! Want to grab coffee?"
                className="w-full px-4 py-3 text-sm border-2 border-gray-200 dark:border-gray-800 bg-white dark:bg-black text-black dark:text-white placeholder:text-gray-400 dark:placeholder:text-gray-600 tracking-tight focus:outline-none focus:border-black dark:focus:border-white transition-colors rounded-lg"
              />
              <p className="text-xs text-gray-400 dark:text-gray-600 mt-2">
                Press Enter to generate
              </p>
            </div>

            <div className="flex gap-3">
              <button
                onClick={handleCancel}
                className="flex-1 px-5 py-3 text-sm border-2 border-gray-200 dark:border-gray-800 tracking-tight hover:bg-gray-50 dark:hover:bg-gray-900 transition-all rounded-lg font-medium"
              >
                Cancel
              </button>
              <button
                onClick={handleGenerate}
                className="flex-1 px-5 py-3 text-sm bg-black dark:bg-white text-white dark:text-black tracking-tight hover:opacity-90 transition-all rounded-lg font-medium shadow-sm"
              >
                Generate
              </button>
            </div>
          </div>
        </div>
      )}
    </main>
  )
}
