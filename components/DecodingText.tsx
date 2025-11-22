'use client'

import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'

interface DecodingTextProps {
  text: string
  duration?: number
  className?: string
}

const GARBLED_CHARS = '!<>-_\\/[]{}—=+*^?#________█▓▒░@#$%&*()[]{}:;▀▄█▌▐░▒▓'

export default function DecodingText({ text, duration = 1000, className = '' }: DecodingTextProps) {
  const [displayText, setDisplayText] = useState('')
  const [isDecoding, setIsDecoding] = useState(true)

  useEffect(() => {
    setIsDecoding(true)
    setDisplayText('')

    const steps = 20 // Number of animation frames
    const interval = duration / steps
    let currentStep = 0

    const decodeInterval = setInterval(() => {
      currentStep++
      const progress = currentStep / steps

      // Generate text with progressively less garbling
      const newText = text.split('').map((char, index) => {
        // Calculate if this character should be revealed yet
        const charProgress = index / text.length

        if (progress > charProgress + 0.3) {
          // Character is fully revealed
          return char
        } else if (progress > charProgress) {
          // Character is being revealed - show some garbled chars
          return Math.random() > 0.5 ? char : GARBLED_CHARS[Math.floor(Math.random() * GARBLED_CHARS.length)]
        } else {
          // Character not revealed yet - show garbled
          return GARBLED_CHARS[Math.floor(Math.random() * GARBLED_CHARS.length)]
        }
      }).join('')

      setDisplayText(newText)

      if (currentStep >= steps) {
        clearInterval(decodeInterval)
        setDisplayText(text)
        setIsDecoding(false)
      }
    }, interval)

    return () => clearInterval(decodeInterval)
  }, [text, duration])

  return (
    <motion.span
      className={className}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.2 }}
    >
      {displayText || text}
    </motion.span>
  )
}
