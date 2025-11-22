'use client'

import Link from 'next/link'

export default function LandingPage() {
  return (
    <main className="min-h-screen bg-white dark:bg-black">
      <div className="max-w-3xl mx-auto px-8 py-16">
        {/* Hero Section */}
        <div className="flex flex-col min-h-[85vh] justify-center">
          <h1 className="text-5xl md:text-6xl font-medium tracking-tight mb-6">
            Vibe Check
          </h1>

          <p className="text-base text-gray-600 dark:text-gray-400 max-w-xl mb-3 tracking-tight">
            Simulate conversations between profiles to discover compatibility
          </p>

          <p className="text-sm text-gray-500 dark:text-gray-500 max-w-lg mb-10 tracking-tight leading-relaxed">
            Upload your iMessage texts, create AI personas, and watch them interact in real-time with detailed compatibility insights
          </p>

          <div>
            <Link
              href="/profiles"
              className="inline-block text-sm hover:opacity-60 transition-opacity underline underline-offset-4"
            >
              Explore Profiles →
            </Link>
          </div>
        </div>

        {/* Features */}
        <div className="grid md:grid-cols-3 gap-8 pb-16 border-t border-gray-200 dark:border-gray-800 pt-16">
          <div className="space-y-2">
            <div className="text-xs text-gray-500 dark:text-gray-500 tracking-tight">01</div>
            <h3 className="text-sm font-medium tracking-tight">Upload Messages</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400 tracking-tight leading-relaxed">
              Import your iMessage conversations to create authentic AI personas
            </p>
          </div>

          <div className="space-y-2">
            <div className="text-xs text-gray-500 dark:text-gray-500 tracking-tight">02</div>
            <h3 className="text-sm font-medium tracking-tight">Generate Conversations</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400 tracking-tight leading-relaxed">
              Watch AI versions interact based on real communication patterns
            </p>
          </div>

          <div className="space-y-2">
            <div className="text-xs text-gray-500 dark:text-gray-500 tracking-tight">03</div>
            <h3 className="text-sm font-medium tracking-tight">Analyze Compatibility</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400 tracking-tight leading-relaxed">
              Get detailed insights into communication styles and connection strength
            </p>
          </div>
        </div>
      </div>
    </main>
  )
}
