import { ReactNode } from 'react'

interface CardProps {
  children: ReactNode
  className?: string
  hover?: boolean
  onClick?: () => void
}

export default function Card({ children, className = '', hover = false, onClick }: CardProps) {
  const baseStyles = 'bg-[var(--surface)] border border-[var(--border)] rounded-lg'
  const hoverStyles = hover ? 'transition-opacity cursor-pointer hover:opacity-60' : ''
  const clickable = onClick ? 'cursor-pointer' : ''

  return (
    <div
      className={`${baseStyles} ${hoverStyles} ${clickable} ${className}`}
      onClick={onClick}
    >
      {children}
    </div>
  )
}
