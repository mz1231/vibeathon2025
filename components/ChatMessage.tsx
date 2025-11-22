import { type Message, type Profile } from '@/lib/mockData'

interface ChatMessageProps {
  message: Message
  profile: Profile
  isUser: boolean
}

export default function ChatMessage({ message, profile, isUser }: ChatMessageProps) {
  return (
    <div className={`flex items-start gap-2 mb-3 ${isUser ? 'justify-end' : 'justify-start'}`}>
      {!isUser && (
        <div
          className="w-5 h-5 rounded-full flex items-center justify-center text-white flex-shrink-0 mt-0.5"
          style={{ backgroundColor: profile.color, fontSize: '10px' }}
        >
          {profile.name[0]}
        </div>
      )}

      <div
        className={`max-w-[70%] px-3 py-2 rounded-2xl ${
          isUser
            ? 'bg-blue-500 text-white'
            : 'bg-gray-100 dark:bg-gray-900 text-black dark:text-white'
        }`}
      >
        <p className="text-xs leading-relaxed tracking-tight">{message.text}</p>
      </div>

      {isUser && (
        <div
          className="w-5 h-5 rounded-full flex items-center justify-center text-white flex-shrink-0 mt-0.5"
          style={{ backgroundColor: profile.color, fontSize: '10px' }}
        >
          {profile.name[0]}
        </div>
      )}
    </div>
  )
}
