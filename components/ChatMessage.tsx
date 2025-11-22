import { type Message, type Profile } from '@/lib/mockData'

interface ChatMessageProps {
  message: Message
  profile: Profile
  isUser: boolean
}

export default function ChatMessage({ message, profile, isUser }: ChatMessageProps) {
  return (
    <div
      className={`flex items-start gap-3 ${isUser ? 'justify-end' : 'justify-start'} ${isUser ? 'animate-slideInRight' : 'animate-slideInLeft'}`}
    >
      {!isUser && (
        <div
          className="w-8 h-8 rounded-full flex items-center justify-center text-white flex-shrink-0 text-sm font-medium shadow-sm"
          style={{ backgroundColor: profile.color }}
        >
          {profile.name[0]}
        </div>
      )}

      <div
        className={`max-w-[65%] px-5 py-3 rounded-3xl ${
          isUser
            ? 'bg-blue-500 text-white shadow-sm'
            : 'bg-white dark:bg-gray-900 text-black dark:text-white border border-gray-200 dark:border-gray-700 shadow-sm'
        }`}
      >
        <p className="text-[15px] leading-[1.6]">{message.text}</p>
      </div>

      {isUser && (
        <div
          className="w-8 h-8 rounded-full flex items-center justify-center text-white flex-shrink-0 text-sm font-medium shadow-sm"
          style={{ backgroundColor: profile.color }}
        >
          {profile.name[0]}
        </div>
      )}
    </div>
  )
}
