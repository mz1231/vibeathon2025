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
      <div className="flex gap-1.5 mb-6 justify-center">
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
            className={`h-px transition-all duration-300 ${
              index === activeIndex
                ? 'w-6 bg-black dark:bg-white'
                : 'w-px bg-gray-300 dark:bg-gray-700'
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
        {insights.map((insight, index) => (
          <div
            key={insight.id}
            className="h-full snap-start flex flex-col justify-center px-8"
          >
            <div className="space-y-4">
              {/* Score Circle */}
              <div className="flex justify-center mb-6">
                <div className="relative w-24 h-24">
                  <svg className="w-full h-full transform -rotate-90">
                    <circle
                      cx="48"
                      cy="48"
                      r="44"
                      stroke="currentColor"
                      strokeWidth="2"
                      fill="none"
                      className="text-gray-200 dark:text-gray-800"
                    />
                    <circle
                      cx="48"
                      cy="48"
                      r="44"
                      stroke="currentColor"
                      strokeWidth="2"
                      fill="none"
                      strokeDasharray={`${2 * Math.PI * 44}`}
                      strokeDashoffset={`${2 * Math.PI * 44 * (1 - insight.score / 100)}`}
                      className={`transition-all duration-1000 ${
                        insight.score >= 80
                          ? 'text-green-500'
                          : insight.score >= 60
                          ? 'text-yellow-500'
                          : 'text-red-500'
                      }`}
                      strokeLinecap="round"
                    />
                  </svg>
                  <div className="absolute inset-0 flex items-center justify-center">
                    <span className="text-2xl font-medium tracking-tight">{insight.score}</span>
                  </div>
                </div>
              </div>

              {/* Title */}
              <h3 className="text-base font-medium text-center tracking-tight">{insight.title}</h3>

              {/* Description */}
              <p className="text-center text-xs text-gray-600 dark:text-gray-400 tracking-tight">
                {insight.description}
              </p>

              {/* Details */}
              <div className="pt-4 border-t border-gray-200 dark:border-gray-800">
                <p className="text-xs leading-relaxed tracking-tight text-gray-600 dark:text-gray-400">
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
