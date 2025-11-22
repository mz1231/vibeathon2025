'use client'

import { useState, useEffect, useRef } from 'react'
import Sidebar from '@/components/Sidebar'
import { Button, Card, Input } from '@/components/ui'
import { type Profile } from '@/lib/mockData'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function ProfileCreationPage() {
  const [profiles, setProfiles] = useState<Profile[]>([])
  const [name, setName] = useState('')
  const [bio, setBio] = useState('')
  const [messagesJson, setMessagesJson] = useState('')
  const [editingId, setEditingId] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

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

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    const reader = new FileReader()
    reader.onload = (event) => {
      try {
        const content = event.target?.result as string
        // Validate it's valid JSON
        JSON.parse(content)
        setMessagesJson(content)
      } catch {
        alert('Invalid JSON file')
      }
    }
    reader.readAsText(file)
  }

  const handleSave = async () => {
    if (!name.trim()) {
      alert('Please enter a name')
      return
    }

    // Validate and parse messages JSON if provided
    let messages: string[] = []
    if (messagesJson.trim()) {
      try {
        const parsed = JSON.parse(messagesJson)
        // Handle different JSON formats
        if (Array.isArray(parsed)) {
          // If it's an array of strings
          if (typeof parsed[0] === 'string') {
            messages = parsed
          }
          // If it's an array of objects with text property
          else if (typeof parsed[0] === 'object' && parsed[0].text) {
            messages = parsed.map((m: { text: string }) => m.text)
          }
        }
      } catch {
        alert('Invalid JSON format for messages')
        return
      }
    }

    setIsLoading(true)

    try {
      // Create profile via API
      const response = await fetch(`${API_URL}/api/profiles`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: name.trim(),
          bio: bio.trim() || null,
          messages: messages.length > 0 ? messages : null,
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to create profile')
      }

      const newProfile = await response.json()

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
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
    } catch (error) {
      console.error('Error saving profile:', error)
      // Fallback to localStorage only
      const newProfile: Profile = {
        id: editingId || `profile-${Date.now()}`,
        name: name.trim(),
        bio: bio.trim() || undefined,
        color: `#${Math.floor(Math.random()*16777215).toString(16).padStart(6, '0')}`,
      }

      if (editingId) {
        const updated = profiles.map(p => p.id === editingId ? newProfile : p)
        saveProfiles(updated)
        setEditingId(null)
      } else {
        saveProfiles([...profiles, newProfile])
      }

      setName('')
      setBio('')
      setMessagesJson('')
    } finally {
      setIsLoading(false)
    }
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
                    <div className="mb-2">
                      <input
                        ref={fileInputRef}
                        type="file"
                        accept=".json"
                        onChange={handleFileUpload}
                        className="hidden"
                        id="json-upload"
                      />
                      <label
                        htmlFor="json-upload"
                        className="inline-flex items-center gap-2 px-3 py-1.5 text-xs bg-[var(--surface)] border border-[var(--border)] rounded-lg cursor-pointer hover:border-[var(--accent)] transition-colors"
                      >
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                          <polyline points="17 8 12 3 7 8" />
                          <line x1="12" y1="3" x2="12" y2="15" />
                        </svg>
                        Upload JSON File
                      </label>
                      {messagesJson && (
                        <span className="ml-2 text-xs text-[var(--accent)]">
                          File loaded
                        </span>
                      )}
                    </div>
                    <textarea
                      value={messagesJson}
                      onChange={(e) => setMessagesJson(e.target.value)}
                      placeholder='["Hey!", "Whats up?", "Not much, you?", ...] or paste your my_texts.json content'
                      className="w-full px-3 py-2 text-sm bg-[var(--surface)] border border-[var(--border)] rounded-lg focus:outline-none focus:border-[var(--accent)] transition-colors resize-none font-mono"
                      rows={6}
                    />
                    <div className="mt-1 text-xs text-[var(--text-secondary)]">
                      Optional: Upload message history (my_texts.json) for better simulation
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
                      disabled={!name.trim() || isLoading}
                      className="flex-1"
                    >
                      {isLoading ? 'Saving...' : editingId ? 'Update Profile' : 'Create Profile'}
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
