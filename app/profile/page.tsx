'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Sidebar from '@/components/Sidebar'
import { Button, Card, Input } from '@/components/ui'
import { motion } from 'framer-motion'

export default function ProfilePage() {
  const router = useRouter()
  const [name, setName] = useState('')
  const [bio, setBio] = useState('')
  const [uploadedFile, setUploadedFile] = useState<File | null>(null)
  const [isProcessing, setIsProcessing] = useState(false)

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      setUploadedFile(file)
    }
  }

  const handleSave = async () => {
    setIsProcessing(true)

    // Simulate processing
    await new Promise(resolve => setTimeout(resolve, 2000))

    // In a real app, this would:
    // 1. Upload the text file to the backend
    // 2. Process it to extract messages
    // 3. Create embeddings
    // 4. Save the profile

    setIsProcessing(false)

    // Navigate back to profiles page
    router.push('/profiles')
  }

  return (
    <div className="flex h-screen bg-[var(--bg)]">
      <Sidebar />

      <main className="flex-1 overflow-y-auto">
        <div className="max-w-3xl mx-auto px-12 py-10">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-2xl font-semibold mb-2 text-[var(--text-primary)]">
              Your Profile
            </h1>
            <p className="text-sm text-[var(--text-secondary)]">
              Create your AI persona by uploading your message history
            </p>
          </div>

          <div className="space-y-6">
            {/* Basic Information Card */}
            <Card className="p-6">
              <h2 className="text-sm font-semibold text-[var(--text-primary)] mb-4">
                Basic Information
              </h2>

              <div className="space-y-4">
                <div>
                  <label className="block text-xs font-medium text-[var(--text-primary)] mb-2">
                    Name
                  </label>
                  <Input
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="Enter your name"
                  />
                </div>

                <div>
                  <label className="block text-xs font-medium text-[var(--text-primary)] mb-2">
                    Bio
                  </label>
                  <textarea
                    value={bio}
                    onChange={(e) => setBio(e.target.value)}
                    placeholder="Tell us about yourself... (optional)"
                    className="w-full px-3 py-2 text-sm bg-[var(--surface)] border border-[var(--border)] rounded-lg focus:outline-none focus:border-[var(--accent)] transition-colors resize-none"
                    rows={4}
                  />
                  <div className="mt-1 text-xs text-[var(--text-secondary)]">
                    {bio.length} / 500 characters
                  </div>
                </div>
              </div>
            </Card>

            {/* Message Upload Card */}
            <Card className="p-6">
              <h2 className="text-sm font-semibold text-[var(--text-primary)] mb-2">
                Message History Upload
              </h2>
              <p className="text-xs text-[var(--text-secondary)] mb-4">
                Upload your iMessage conversation export to train your AI persona
              </p>

              <div className="space-y-4">
                {/* Upload Area */}
                <div className="border-2 border-dashed border-[var(--border)] rounded-lg p-8 text-center hover:border-[var(--accent)] transition-colors">
                  <input
                    type="file"
                    id="file-upload"
                    accept=".txt,.json,.csv"
                    onChange={handleFileUpload}
                    className="hidden"
                  />

                  <label
                    htmlFor="file-upload"
                    className="cursor-pointer"
                  >
                    {uploadedFile ? (
                      <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="space-y-2"
                      >
                        <div className="text-4xl mb-2">📄</div>
                        <div className="text-sm text-[var(--text-primary)] font-medium">
                          {uploadedFile.name}
                        </div>
                        <div className="text-xs text-[var(--text-secondary)]">
                          {(uploadedFile.size / 1024).toFixed(2)} KB
                        </div>
                        <div className="text-xs text-[var(--accent)] hover:underline mt-2">
                          Change file
                        </div>
                      </motion.div>
                    ) : (
                      <div className="space-y-2">
                        <div className="text-4xl mb-2">📤</div>
                        <div className="text-sm text-[var(--text-primary)] font-medium">
                          Click to upload message history
                        </div>
                        <div className="text-xs text-[var(--text-secondary)]">
                          Supports .txt, .json, or .csv files
                        </div>
                      </div>
                    )}
                  </label>
                </div>

                {/* Instructions */}
                <div className="bg-[var(--bg)] border border-[var(--border)] rounded-lg p-4">
                  <h3 className="text-xs font-semibold text-[var(--text-primary)] mb-2">
                    How to export your iMessages:
                  </h3>
                  <ol className="text-xs text-[var(--text-secondary)] space-y-1 list-decimal list-inside">
                    <li>On Mac, open Messages app</li>
                    <li>Select a conversation</li>
                    <li>Use a third-party tool or script to export to text</li>
                    <li>Upload the exported file here</li>
                  </ol>
                </div>
              </div>
            </Card>

            {/* Save Button */}
            <div className="flex items-center justify-between pt-4">
              <Button
                variant="ghost"
                size="md"
                onClick={() => router.push('/profiles')}
              >
                Cancel
              </Button>

              <Button
                variant="primary"
                size="md"
                onClick={handleSave}
                disabled={!name || !uploadedFile || isProcessing}
              >
                {isProcessing ? (
                  <span className="flex items-center gap-2">
                    <motion.div
                      className="w-3 h-3 border-2 border-white border-t-transparent rounded-full"
                      animate={{ rotate: 360 }}
                      transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                    />
                    Processing...
                  </span>
                ) : (
                  'Save Profile'
                )}
              </Button>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
