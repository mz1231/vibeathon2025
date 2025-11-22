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
    <main className="min-h-screen bg-white dark:bg-black px-8 py-12">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-12">
          <h1 className="text-3xl font-medium tracking-tight mb-2">Select Profiles</h1>
          <p className="text-sm text-gray-600 dark:text-gray-400 tracking-tight">
            Choose two profiles to simulate a conversation
          </p>
        </div>

        {/* Selection Indicator */}
        {selectedProfiles.length > 0 && (
          <div className="mb-8 flex items-center gap-3">
            <span className="text-xs text-gray-500 tracking-tight">Selected:</span>
            {selectedProfiles.map(profile => (
              <div
                key={profile.id}
                className="flex items-center gap-2 text-xs tracking-tight"
              >
                <div
                  className="w-2 h-2 rounded-full"
                  style={{ backgroundColor: profile.color }}
                />
                <span>{profile.name}</span>
              </div>
            ))}
          </div>
        )}

        {/* Profile Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {mockProfiles.map(profile => {
            const isSelected = selectedProfiles.find(p => p.id === profile.id)
            const isDisabled = selectedProfiles.length === 2 && !isSelected

            return (
              <button
                key={profile.id}
                onClick={() => handleProfileClick(profile)}
                disabled={isDisabled}
                className={`
                  group relative aspect-[4/5] transition-all duration-200
                  ${isSelected
                    ? 'opacity-100'
                    : 'opacity-100 hover:opacity-60'
                  }
                  ${isDisabled ? 'opacity-30 cursor-not-allowed' : 'cursor-pointer'}
                `}
              >
                {/* Profile Card Content */}
                <div className="absolute inset-0 p-4 flex flex-col justify-between border border-gray-200 dark:border-gray-800">
                  {/* Avatar Circle */}
                  <div className="flex justify-center pt-4">
                    <div
                      className="w-16 h-16 rounded-full flex items-center justify-center text-white text-lg"
                      style={{ backgroundColor: profile.color }}
                    >
                      {profile.name[0]}
                    </div>
                  </div>

                  {/* Name */}
                  <div className="text-center pb-2">
                    <h3 className="text-sm font-medium tracking-tight">{profile.name}</h3>
                  </div>
                </div>

                {/* Selection Indicator */}
                {isSelected && (
                  <div className="absolute top-2 right-2 w-2 h-2 rounded-full bg-black dark:bg-white" />
                )}
              </button>
            )
          })}
        </div>
      </div>

      {/* Generation Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/30 dark:bg-white/10 flex items-center justify-center z-50 px-6">
          <div className="bg-white dark:bg-black border border-gray-200 dark:border-gray-800 max-w-md w-full p-6">
            <h2 className="text-lg font-medium tracking-tight mb-6">Generate Conversation</h2>

            <div className="mb-6">
              <p className="text-xs text-gray-500 dark:text-gray-500 mb-3 tracking-tight">
                Selected profiles
              </p>
              <div className="flex gap-3">
                {selectedProfiles.map(profile => (
                  <div key={profile.id} className="flex items-center gap-2 text-sm">
                    <div
                      className="w-6 h-6 rounded-full flex items-center justify-center text-white text-xs"
                      style={{ backgroundColor: profile.color }}
                    >
                      {profile.name[0]}
                    </div>
                    <span className="tracking-tight">{profile.name}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="mb-6">
              <label className="block text-xs text-gray-500 dark:text-gray-500 mb-2 tracking-tight">
                Conversation Starter (Optional)
              </label>
              <input
                type="text"
                value={conversationStarter}
                onChange={(e) => setConversationStarter(e.target.value)}
                placeholder="e.g., Hey! Want to grab coffee?"
                className="w-full px-3 py-2 text-sm border border-gray-200 dark:border-gray-800 bg-transparent tracking-tight focus:outline-none focus:border-gray-400 dark:focus:border-gray-600 transition-colors"
              />
            </div>

            <div className="flex gap-3">
              <button
                onClick={handleCancel}
                className="flex-1 px-4 py-2 text-sm border border-gray-200 dark:border-gray-800 tracking-tight hover:opacity-60 transition-opacity"
              >
                Cancel
              </button>
              <button
                onClick={handleGenerate}
                className="flex-1 px-4 py-2 text-sm bg-black dark:bg-white text-white dark:text-black tracking-tight hover:opacity-90 transition-opacity"
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
