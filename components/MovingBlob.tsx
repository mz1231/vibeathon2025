'use client'

import { motion, useAnimation } from 'framer-motion'
import { useEffect } from 'react'

interface MovingBlobProps {
  color: 'black' | 'white'
  isActive: boolean
  containerWidth: number
  containerHeight: number
}

export default function MovingBlob({ color, isActive, containerWidth, containerHeight }: MovingBlobProps) {
  const controls = useAnimation()

  useEffect(() => {
    const animateBlob = async () => {
      // Generate random path points
      const generatePath = () => {
        const padding = 50
        return {
          x: Math.random() * (containerWidth - padding * 2) + padding,
          y: Math.random() * (containerHeight - padding * 2) + padding,
        }
      }

      while (true) {
        const target = generatePath()
        await controls.start({
          x: target.x,
          y: target.y,
          transition: {
            duration: 3 + Math.random() * 2, // 3-5 seconds per move
            ease: [0.43, 0.13, 0.23, 0.96], // Custom easing for smooth, organic motion
          },
        })
      }
    }

    animateBlob()
  }, [controls, containerWidth, containerHeight])

  const blobSize = isActive ? 16 : 12
  const glowSize = isActive ? 24 : 16

  return (
    <motion.div
      animate={controls}
      initial={{ x: containerWidth / 2, y: containerHeight / 2 }}
      className="absolute pointer-events-none"
      style={{ left: -blobSize / 2, top: -blobSize / 2 }}
    >
      {/* Glow effect */}
      <motion.div
        className="absolute rounded-full blur-md"
        style={{
          width: glowSize,
          height: glowSize,
          left: (blobSize - glowSize) / 2,
          top: (blobSize - glowSize) / 2,
          backgroundColor: color === 'black' ? 'rgba(0, 0, 0, 0.3)' : 'rgba(255, 255, 255, 0.5)',
        }}
        animate={{
          scale: isActive ? [1, 1.2, 1] : 1,
          opacity: isActive ? [0.3, 0.6, 0.3] : 0.2,
        }}
        transition={{
          duration: 2,
          repeat: Infinity,
          ease: 'easeInOut',
        }}
      />

      {/* Main blob */}
      <motion.div
        className="rounded-full"
        style={{
          width: blobSize,
          height: blobSize,
          backgroundColor: color === 'black' ? '#000000' : '#FFFFFF',
          border: color === 'white' ? '1px solid var(--border)' : 'none',
          boxShadow: color === 'black'
            ? '0 2px 8px rgba(0, 0, 0, 0.3)'
            : '0 2px 8px rgba(0, 0, 0, 0.1)',
        }}
        animate={{
          scale: isActive ? [1, 1.1, 1] : 1,
        }}
        transition={{
          duration: 2,
          repeat: Infinity,
          ease: 'easeInOut',
        }}
      />
    </motion.div>
  )
}
