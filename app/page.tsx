'use client'

import Link from 'next/link'
import { Button } from '@/components/ui'

export default function LandingPage() {
  return (
    <main className="min-h-screen bg-[var(--bg)]">
      <div className="max-w-4xl mx-auto px-8 py-16">
        {/* Hero Section */}
        <div className="flex flex-col min-h-[85vh] justify-center">
          <h1 className="text-5xl md:text-6xl font-semibold mb-6 text-[var(--text-primary)]">
            Vibe Check
          </h1>

          <p className="text-lg text-[var(--text-primary)] max-w-xl mb-3">
            Create profiles and simulate conversations to analyze compatibility
          </p>

          <p className="text-sm text-[var(--text-secondary)] max-w-lg mb-10 leading-relaxed">
            Build communication profiles, run simulated conversations between any two profiles, and get detailed compatibility insights
          </p>

          <div className="flex gap-3">
            <Link href="/profile">
              <Button variant="primary" size="md">
                Create Profile →
              </Button>
            </Link>
            <Link href="/profiles">
              <Button variant="secondary" size="md">
                Browse Profiles
              </Button>
            </Link>
          </div>
        </div>

        {/* Features */}
        <div className="grid md:grid-cols-3 gap-10 pb-16 border-t border-[var(--border)] pt-16">
          <div className="space-y-3">
            <div className="text-xs text-[var(--text-secondary)] font-medium">01</div>
            <h3 className="text-base font-semibold text-[var(--text-primary)]">Create Profiles</h3>
            <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
              Build communication profiles with names, bios, and optional message history
            </p>
          </div>

          <div className="space-y-3">
            <div className="text-xs text-[var(--text-secondary)] font-medium">02</div>
            <h3 className="text-base font-semibold text-[var(--text-primary)]">Simulate Conversations</h3>
            <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
              Select any two profiles to generate and analyze their conversation dynamics
            </p>
          </div>

          <div className="space-y-3">
            <div className="text-xs text-[var(--text-secondary)] font-medium">03</div>
            <h3 className="text-base font-semibold text-[var(--text-primary)]">Analyze Compatibility</h3>
            <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
              Review compatibility scores and insights on communication styles
            </p>
          </div>
        </div>
      </div>
    </main>
  )
}
