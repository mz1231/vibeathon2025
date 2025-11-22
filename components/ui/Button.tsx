import { ButtonHTMLAttributes, ReactNode } from 'react'

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode
  variant?: 'primary' | 'secondary' | 'ghost'
  size?: 'sm' | 'md' | 'lg'
}

export default function Button({
  children,
  variant = 'primary',
  size = 'md',
  className = '',
  ...props
}: ButtonProps) {
  const baseStyles = 'font-medium rounded-md transition-opacity hover:opacity-90 disabled:opacity-40 disabled:cursor-not-allowed'

  const variants = {
    primary: 'bg-[var(--accent)] text-white hover:bg-[var(--accent-hover)]',
    secondary: 'border border-[var(--border)] bg-[var(--surface)] text-[var(--text-primary)]',
    ghost: 'text-[var(--text-secondary)] hover:text-[var(--text-primary)]'
  }

  const sizes = {
    sm: 'px-3 py-1.5 text-xs',
    md: 'px-4 py-2 text-sm',
    lg: 'px-5 py-2.5 text-base'
  }

  return (
    <button
      className={`${baseStyles} ${variants[variant]} ${sizes[size]} ${className}`}
      {...props}
    >
      {children}
    </button>
  )
}
