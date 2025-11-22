'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'

interface NavItem {
  label: string
  href: string
  icon: React.ReactNode
}

const navItems: NavItem[] = [
  {
    label: 'Matching',
    href: '/profiles',
    icon: (
      <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor">
        <rect x="2" y="2" width="5" height="5" strokeWidth="1.5" />
        <rect x="9" y="2" width="5" height="5" strokeWidth="1.5" />
        <rect x="2" y="9" width="5" height="5" strokeWidth="1.5" />
        <rect x="9" y="9" width="5" height="5" strokeWidth="1.5" />
      </svg>
    )
  },
  {
    label: 'Profile',
    href: '/profile',
    icon: (
      <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor">
        <circle cx="8" cy="6" r="3" strokeWidth="1.5" />
        <path d="M2 14c0-3.314 2.686-6 6-6s6 2.686 6 6" strokeWidth="1.5" />
      </svg>
    )
  },
  {
    label: 'Settings',
    href: '/settings',
    icon: (
      <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor">
        <circle cx="8" cy="8" r="2" strokeWidth="1.5" />
        <path d="M8 2v1m0 10v1M2 8h1m10 0h1M4 4l.707.707m6.586 6.586L12 12M12 4l-.707.707M4.707 11.293L4 12" strokeWidth="1.5" />
      </svg>
    )
  }
]

export default function Sidebar() {
  const pathname = usePathname()

  return (
    <aside className="w-[220px] bg-[var(--sidebar-bg)] border-r border-[var(--border)] h-screen flex flex-col">
      {/* Logo/Brand */}
      <div className="px-5 py-6 border-b border-[var(--border)]">
        <Link href="/" className="text-sm font-semibold text-[var(--text-primary)]">
          Vibe Check
        </Link>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4">
        <div className="space-y-1">
          {navItems.map((item) => {
            const isActive = pathname === item.href || pathname?.startsWith(item.href + '/')

            return (
              <Link
                key={item.href}
                href={item.href}
                className={`
                  flex items-center gap-3 px-3 py-2 rounded text-sm
                  transition-colors
                  ${
                    isActive
                      ? 'bg-[var(--surface)] text-[var(--text-primary)] font-medium'
                      : 'text-[var(--text-secondary)] hover:bg-[var(--surface)] hover:text-[var(--text-primary)]'
                  }
                `}
              >
                {item.icon}
                {item.label}
              </Link>
            )
          })}
        </div>
      </nav>

      {/* Footer */}
      <div className="px-5 py-4 border-t border-[var(--border)]">
        <p className="text-xs text-[var(--text-secondary)]">
          Built for Princeton Vibeathon 2025
        </p>
      </div>
    </aside>
  )
}
