'use client'

import { useState, useEffect } from 'react'
import Sidebar from '@/components/Sidebar'
import { Card } from '@/components/ui'

export default function SettingsPage() {
  const [theme, setTheme] = useState<'light' | 'dark' | 'system'>('system')

  useEffect(() => {
    // Load saved theme preference
    const saved = localStorage.getItem('theme') as 'light' | 'dark' | 'system' | null
    if (saved) {
      setTheme(saved)
      applyTheme(saved)
    } else {
      // Default to system preference
      applyTheme('system')
    }
  }, [])

  const applyTheme = (newTheme: 'light' | 'dark' | 'system') => {
    const root = document.documentElement

    if (newTheme === 'system') {
      // Use system preference
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
      root.classList.remove('light', 'dark')
      root.classList.add(prefersDark ? 'dark' : 'light')
    } else {
      root.classList.remove('light', 'dark')
      root.classList.add(newTheme)
    }

    localStorage.setItem('theme', newTheme)
  }

  const handleThemeChange = (newTheme: 'light' | 'dark' | 'system') => {
    setTheme(newTheme)
    applyTheme(newTheme)
  }

  return (
    <div className="flex h-screen bg-[var(--bg)]">
      <Sidebar />

      <main className="flex-1 overflow-y-auto">
        <div className="max-w-3xl mx-auto px-12 py-10">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-2xl font-semibold mb-2 text-[var(--text-primary)]">
              Settings
            </h1>
            <p className="text-sm text-[var(--text-secondary)]">
              Customize your experience
            </p>
          </div>

          {/* Appearance Section */}
          <div className="space-y-6">
            <Card className="p-6">
              <h2 className="text-sm font-semibold text-[var(--text-primary)] mb-4">
                Appearance
              </h2>

              <div className="space-y-3">
                <label className="block text-xs font-medium text-[var(--text-primary)] mb-3">
                  Theme
                </label>

                <div className="grid grid-cols-3 gap-3">
                  {/* Light */}
                  <button
                    onClick={() => handleThemeChange('light')}
                    className={`p-4 border rounded-lg transition-all ${
                      theme === 'light'
                        ? 'border-[var(--accent)] bg-[var(--accent)]/5 ring-2 ring-[var(--accent)]'
                        : 'border-[var(--border)] hover:border-[var(--accent)]'
                    }`}
                  >
                    <div className="flex flex-col items-center gap-2">
                      <div className="w-12 h-8 rounded border border-gray-300 bg-white flex items-center justify-center">
                        <div className="w-8 h-4 rounded bg-gray-200"></div>
                      </div>
                      <span className="text-xs font-medium text-[var(--text-primary)]">Light</span>
                    </div>
                  </button>

                  {/* Dark */}
                  <button
                    onClick={() => handleThemeChange('dark')}
                    className={`p-4 border rounded-lg transition-all ${
                      theme === 'dark'
                        ? 'border-[var(--accent)] bg-[var(--accent)]/5 ring-2 ring-[var(--accent)]'
                        : 'border-[var(--border)] hover:border-[var(--accent)]'
                    }`}
                  >
                    <div className="flex flex-col items-center gap-2">
                      <div className="w-12 h-8 rounded border border-gray-700 bg-gray-900 flex items-center justify-center">
                        <div className="w-8 h-4 rounded bg-gray-700"></div>
                      </div>
                      <span className="text-xs font-medium text-[var(--text-primary)]">Dark</span>
                    </div>
                  </button>

                  {/* System */}
                  <button
                    onClick={() => handleThemeChange('system')}
                    className={`p-4 border rounded-lg transition-all ${
                      theme === 'system'
                        ? 'border-[var(--accent)] bg-[var(--accent)]/5 ring-2 ring-[var(--accent)]'
                        : 'border-[var(--border)] hover:border-[var(--accent)]'
                    }`}
                  >
                    <div className="flex flex-col items-center gap-2">
                      <div className="w-12 h-8 rounded border border-gray-300 bg-gradient-to-r from-white to-gray-900 flex items-center justify-center">
                        <div className="w-8 h-4 rounded bg-gradient-to-r from-gray-200 to-gray-700"></div>
                      </div>
                      <span className="text-xs font-medium text-[var(--text-primary)]">System</span>
                    </div>
                  </button>
                </div>

                <p className="text-xs text-[var(--text-secondary)] mt-3">
                  {theme === 'system'
                    ? 'Theme will match your system preferences'
                    : `Using ${theme} theme`}
                </p>
              </div>
            </Card>

            {/* About Section */}
            <Card className="p-6">
              <h2 className="text-sm font-semibold text-[var(--text-primary)] mb-4">
                About
              </h2>
              <div className="space-y-2 text-xs text-[var(--text-secondary)]">
                <p>Vibe Check - Conversation Compatibility Simulator</p>
                <p>Built for Princeton Claude Vibeathon 2025</p>
              </div>
            </Card>
          </div>
        </div>
      </main>
    </div>
  )
}
