'use client'

import { useEffect, useRef, useState } from 'react'
import { type Insight } from '@/lib/mockData'

interface InsightsPanelProps {
  insights: Insight[]
}

export default function InsightsPanel({ insights }: InsightsPanelProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const [activeIndex, setActiveIndex] = useState(0)

  useEffect(() => {
    const container = containerRef.current
    if (!container) return

    const handleScroll = () => {
      const scrollPosition = container.scrollTop
      const sectionHeight = container.clientHeight
      const newIndex = Math.round(scrollPosition / sectionHeight)
      setActiveIndex(Math.min(newIndex, insights.length - 1))
    }

    container.addEventListener('scroll', handleScroll)
    return () => container.removeEventListener('scroll', handleScroll)
  }, [insights.length])

  return (
    <div className="h-full flex flex-col">
      {/* Scroll Indicators */}
      <div className="flex gap-2 mb-6 justify-center">
        {insights.map((_, index) => (
          <button
            key={index}
            onClick={() => {
              const container = containerRef.current
              if (container) {
                container.scrollTo({
                  top: index * container.clientHeight,
                  behavior: 'smooth',
                })
              }
            }}
            className={`h-0.5 transition-all duration-300 rounded-full ${
              index === activeIndex
                ? 'w-6 bg-[var(--accent)]'
                : 'w-1 bg-[var(--border)]'
            }`}
          />
        ))}
      </div>

      {/* Insights Container */}
      <div
        ref={containerRef}
        className="flex-1 overflow-y-scroll snap-y snap-mandatory scroll-smooth"
        style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}
      >
        {insights.map((insight) => (
          <div
            key={insight.id}
            className="h-full snap-start flex flex-col justify-center px-8"
          >
            <div className="space-y-4">
              {/* Score Circle */}
              <div className="flex justify-center mb-6">
                <div className="relative w-28 h-28">
                  <svg className="w-full h-full transform -rotate-90">
                    <circle
                      cx="56"
                      cy="56"
                      r="52"
                      stroke="currentColor"
                      strokeWidth="1.5"
                      fill="none"
                      className="text-[var(--border)]"
                    />
                    <circle
                      cx="56"
                      cy="56"
                      r="52"
                      stroke="currentColor"
                      strokeWidth="1.5"
                      fill="none"
                      strokeDasharray={`${2 * Math.PI * 52}`}
                      strokeDashoffset={`${2 * Math.PI * 52 * (1 - insight.score / 100)}`}
                      className={`transition-all duration-1000 ${
                        insight.score >= 80
                          ? 'text-[var(--success)]'
                          : insight.score >= 60
                          ? 'text-[var(--accent)]'
                          : 'text-[var(--error)]'
                      }`}
                      strokeLinecap="round"
                    />
                  </svg>
                  <div className="absolute inset-0 flex items-center justify-center">
                    <span className="text-3xl font-semibold text-[var(--text-primary)]">{insight.score}</span>
                  </div>
                </div>
              </div>

              {/* Title */}
              <h3 className="text-base font-semibold text-center text-[var(--text-primary)]">{insight.title}</h3>

              {/* Description */}
              <p className="text-center text-xs text-[var(--text-secondary)] leading-relaxed">
                {insight.description}
              </p>

              {/* Details */}
              <div className="pt-4 border-t border-[var(--border)]">
                <p className="text-xs leading-relaxed text-[var(--text-secondary)]">
                  {insight.details}
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>

      <style jsx>{`
        div::-webkit-scrollbar {
          display: none;
        }
      `}</style>
    </div>
  )
}
