import { type Message, type Profile } from '@/lib/mockData'

interface ChatMessageProps {
  message: Message
  profile: Profile
  isUser: boolean
}

export default function ChatMessage({ message, profile, isUser }: ChatMessageProps) {
  return (
    <div className={`flex items-start gap-2.5 mb-4 animate-fadeIn ${isUser ? 'justify-end' : 'justify-start'}`}>
      {!isUser && (
        <div
          className="w-6 h-6 rounded-full flex items-center justify-center text-white flex-shrink-0 mt-0.5 font-medium"
          style={{ backgroundColor: profile.color, fontSize: '11px' }}
        >
          {profile.name[0]}
        </div>
      )}

      <div
        className={`max-w-[70%] px-3.5 py-2.5 rounded-lg border ${
          isUser
            ? 'bg-[#F3F7FF] dark:bg-[#1a2332] border-[#e3edff] dark:border-[#2a3a52] text-[var(--text-primary)]'
            : 'bg-[var(--surface)] border-[var(--border)] text-[var(--text-primary)]'
        }`}
      >
        <p className="text-sm leading-relaxed">{message.text}</p>
      </div>

      {isUser && (
        <div
          className="w-6 h-6 rounded-full flex items-center justify-center text-white flex-shrink-0 mt-0.5 font-medium"
          style={{ backgroundColor: profile.color, fontSize: '11px' }}
        >
          {profile.name[0]}
        </div>
      )}
    </div>
  )
}
