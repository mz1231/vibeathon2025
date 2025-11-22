'use client'

import { useState, useEffect } from 'react'
import Sidebar from '@/components/Sidebar'
import { Button, Card, Input } from '@/components/ui'
import { type Profile } from '@/lib/mockData'

export default function ProfileCreationPage() {
  const [profiles, setProfiles] = useState<Profile[]>([])
  const [name, setName] = useState('')
  const [bio, setBio] = useState('')
  const [messagesJson, setMessagesJson] = useState('')
  const [editingId, setEditingId] = useState<string | null>(null)

  // Load profiles from localStorage on mount
  useEffect(() => {
    const stored = localStorage.getItem('createdProfiles')
    if (stored) {
      setProfiles(JSON.parse(stored))
    }
  }, [])

  const saveProfiles = (newProfiles: Profile[]) => {
    setProfiles(newProfiles)
    localStorage.setItem('createdProfiles', JSON.stringify(newProfiles))
  }

  const handleSave = () => {
    if (!name.trim()) {
      alert('Please enter a name')
      return
    }

    // Validate JSON if provided
    if (messagesJson.trim()) {
      try {
        JSON.parse(messagesJson)
      } catch (e) {
        alert('Invalid JSON format for messages')
        return
      }
    }

    const newProfile: Profile = {
      id: editingId || `profile-${Date.now()}`,
      name: name.trim(),
      bio: bio.trim() || undefined,
      color: `#${Math.floor(Math.random()*16777215).toString(16)}`, // Random color
    }

    if (editingId) {
      // Update existing
      const updated = profiles.map(p => p.id === editingId ? newProfile : p)
      saveProfiles(updated)
      setEditingId(null)
    } else {
      // Create new
      saveProfiles([...profiles, newProfile])
    }

    // Reset form
    setName('')
    setBio('')
    setMessagesJson('')
  }

  const handleEdit = (profile: Profile) => {
    setEditingId(profile.id)
    setName(profile.name)
    setBio(profile.bio || '')
    setMessagesJson('') // Messages stored separately if needed
  }

  const handleDelete = (id: string) => {
    if (confirm('Are you sure you want to delete this profile?')) {
      saveProfiles(profiles.filter(p => p.id !== id))
    }
  }

  const handleCancel = () => {
    setEditingId(null)
    setName('')
    setBio('')
    setMessagesJson('')
  }

  return (
    <div className="flex h-screen bg-[var(--bg)]">
      <Sidebar />

      <main className="flex-1 overflow-y-auto">
        <div className="max-w-5xl mx-auto px-12 py-10">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-2xl font-semibold mb-2 text-[var(--text-primary)]">
              Create Profiles
            </h1>
            <p className="text-sm text-[var(--text-secondary)]">
              Create profiles to simulate conversations and analyze compatibility
            </p>
          </div>

          <div className="grid grid-cols-2 gap-8">
            {/* Left: Creation Form */}
            <div>
              <Card className="p-6">
                <h2 className="text-sm font-semibold text-[var(--text-primary)] mb-4">
                  {editingId ? 'Edit Profile' : 'New Profile'}
                </h2>

                <div className="space-y-4">
                  <div>
                    <label className="block text-xs font-medium text-[var(--text-primary)] mb-2">
                      Name *
                    </label>
                    <Input
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      placeholder="Enter profile name"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-medium text-[var(--text-primary)] mb-2">
                      Bio
                    </label>
                    <textarea
                      value={bio}
                      onChange={(e) => setBio(e.target.value)}
                      placeholder="Brief description of communication style..."
                      className="w-full px-3 py-2 text-sm bg-[var(--surface)] border border-[var(--border)] rounded-lg focus:outline-none focus:border-[var(--accent)] transition-colors resize-none"
                      rows={3}
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-medium text-[var(--text-primary)] mb-2">
                      Messages (JSON Format)
                    </label>
                    <textarea
                      value={messagesJson}
                      onChange={(e) => setMessagesJson(e.target.value)}
                      placeholder='[{"text": "Hey!", "sender": "profileA"}, ...]'
                      className="w-full px-3 py-2 text-sm bg-[var(--surface)] border border-[var(--border)] rounded-lg focus:outline-none focus:border-[var(--accent)] transition-colors resize-none font-mono"
                      rows={6}
                    />
                    <div className="mt-1 text-xs text-[var(--text-secondary)]">
                      Optional: Upload message history for better simulation
                    </div>
                  </div>

                  <div className="flex gap-2 pt-2">
                    {editingId && (
                      <Button
                        variant="ghost"
                        size="md"
                        onClick={handleCancel}
                      >
                        Cancel
                      </Button>
                    )}
                    <Button
                      variant="primary"
                      size="md"
                      onClick={handleSave}
                      disabled={!name.trim()}
                      className="flex-1"
                    >
                      {editingId ? 'Update Profile' : 'Create Profile'}
                    </Button>
                  </div>
                </div>
              </Card>
            </div>

            {/* Right: Created Profiles List */}
            <div>
              <h2 className="text-sm font-semibold text-[var(--text-primary)] mb-4">
                Created Profiles ({profiles.length})
              </h2>

              {profiles.length === 0 ? (
                <Card className="p-8 text-center">
                  <div className="text-sm text-[var(--text-secondary)]">
                    No profiles created yet. Create one to get started!
                  </div>
                </Card>
              ) : (
                <div className="space-y-3">
                  {profiles.map((profile) => (
                    <Card key={profile.id} className="p-4">
                      <div className="flex items-start gap-3">
                        <div
                          className="w-10 h-10 rounded-full flex items-center justify-center text-white font-medium flex-shrink-0"
                          style={{ backgroundColor: profile.color }}
                        >
                          {profile.name[0]}
                        </div>

                        <div className="flex-1 min-w-0">
                          <h3 className="text-sm font-medium text-[var(--text-primary)] mb-1">
                            {profile.name}
                          </h3>
                          <p className="text-xs text-[var(--text-secondary)] line-clamp-2">
                            {profile.bio || 'No bio'}
                          </p>
                        </div>

                        <div className="flex gap-2">
                          <button
                            onClick={() => handleEdit(profile)}
                            className="text-xs text-[var(--accent)] hover:underline"
                          >
                            Edit
                          </button>
                          <button
                            onClick={() => handleDelete(profile.id)}
                            className="text-xs text-[var(--error)] hover:underline"
                          >
                            Delete
                          </button>
                        </div>
                      </div>
                    </Card>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
