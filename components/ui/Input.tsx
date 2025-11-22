import { InputHTMLAttributes } from 'react'

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string
}

export default function Input({ label, className = '', ...props }: InputProps) {
  return (
    <div className="w-full">
      {label && (
        <label className="block text-xs text-[var(--text-secondary)] mb-2 font-medium">
          {label}
        </label>
      )}
      <input
        className={`
          w-full px-3 py-2 text-sm
          bg-[var(--surface)]
          border border-[var(--border)]
          rounded-md
          text-[var(--text-primary)]
          placeholder:text-[var(--text-secondary)]
          focus:outline-none focus:border-[var(--accent)]
          transition-colors
          ${className}
        `}
        {...props}
      />
    </div>
  )
}
