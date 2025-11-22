'use client'

import Link from 'next/link'

export default function LandingPage() {
  return (
    <main className="min-h-screen bg-white dark:bg-black">
      <div className="max-w-4xl mx-auto px-6 py-20">
        {/* Hero Section */}
        <div className="flex flex-col min-h-[80vh] justify-center">
          <h1 className="text-6xl md:text-7xl font-semibold tracking-tight mb-8">
            Vibe Check
          </h1>

          <p className="text-xl text-gray-600 dark:text-gray-400 max-w-2xl mb-4 leading-relaxed">
            Simulate conversations between profiles to discover compatibility
          </p>

          <p className="text-base text-gray-500 dark:text-gray-500 max-w-xl mb-12 leading-relaxed">
            Upload your iMessage texts, create AI personas, and watch them interact in real-time with detailed compatibility insights
          </p>

          <div>
            <Link
              href="/profiles"
              className="inline-flex items-center gap-2 px-6 py-3 bg-black dark:bg-white text-white dark:text-black text-sm font-medium rounded-lg hover:opacity-90 transition-opacity"
            >
              Get Started
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <path d="M6 3L11 8L6 13" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </Link>
          </div>
        </div>

        {/* Features */}
        <div className="grid md:grid-cols-3 gap-12 pb-20 border-t border-gray-200 dark:border-gray-800 pt-20">
          <div className="space-y-3">
            <div className="text-sm text-gray-400 dark:text-gray-600 font-mono">01</div>
            <h3 className="text-lg font-semibold">Upload Messages</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
              Import your iMessage conversations to create authentic AI personas
            </p>
          </div>

          <div className="space-y-3">
            <div className="text-sm text-gray-400 dark:text-gray-600 font-mono">02</div>
            <h3 className="text-lg font-semibold">Generate Conversations</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
              Watch AI versions interact based on real communication patterns
            </p>
          </div>

          <div className="space-y-3">
            <div className="text-sm text-gray-400 dark:text-gray-600 font-mono">03</div>
            <h3 className="text-lg font-semibold">Analyze Compatibility</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
              Get detailed insights into communication styles and connection strength
            </p>
          </div>
        </div>
      </div>
    </main>
  )
}
