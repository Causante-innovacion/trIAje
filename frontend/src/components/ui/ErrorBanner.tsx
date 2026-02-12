import { X } from 'lucide-react'

interface ErrorBannerProps {
  message: string
  onDismiss: () => void
}

export function ErrorBanner({ message, onDismiss }: ErrorBannerProps) {
  return (
    <div className="bg-red-50 border-b border-red-200 px-4 py-3 animate-slide-down">
      <div className="max-w-6xl mx-auto flex items-center justify-between">
        <span className="text-red-800 text-sm font-medium">{message}</span>
        <button
          onClick={onDismiss}
          className="text-red-400 hover:text-red-600 transition-colors p-1 rounded-full hover:bg-red-100"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
    </div>
  )
}
