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
            Simulate conversations between profiles to discover compatibility
          </p>

          <p className="text-sm text-[var(--text-secondary)] max-w-lg mb-10 leading-relaxed">
            Upload your iMessage texts, create AI personas, and watch them interact in real-time with detailed compatibility insights
          </p>

          <div>
            <Link href="/profiles">
              <Button variant="primary" size="md">
                Explore Profiles →
              </Button>
            </Link>
          </div>
        </div>

        {/* Features */}
        <div className="grid md:grid-cols-3 gap-10 pb-16 border-t border-[var(--border)] pt-16">
          <div className="space-y-3">
            <div className="text-xs text-[var(--text-secondary)] font-medium">01</div>
            <h3 className="text-base font-semibold text-[var(--text-primary)]">Upload Messages</h3>
            <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
              Import your iMessage conversations to create authentic AI personas
            </p>
          </div>

          <div className="space-y-3">
            <div className="text-xs text-[var(--text-secondary)] font-medium">02</div>
            <h3 className="text-base font-semibold text-[var(--text-primary)]">Generate Conversations</h3>
            <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
              Watch AI versions interact based on real communication patterns
            </p>
          </div>

          <div className="space-y-3">
            <div className="text-xs text-[var(--text-secondary)] font-medium">03</div>
            <h3 className="text-base font-semibold text-[var(--text-primary)]">Analyze Compatibility</h3>
            <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
              Get detailed insights into communication styles and connection strength
            </p>
          </div>
        </div>
      </div>
    </main>
  )
}
