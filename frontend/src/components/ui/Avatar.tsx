import clsx from 'clsx'
import { Bot } from 'lucide-react'

interface AvatarProps {
  size?: 'sm' | 'md' | 'lg'
  className?: string
}

export function Avatar({ size = 'md', className }: AvatarProps) {
  const sizes = {
    sm: 'w-8 h-8',
    md: 'w-10 h-10',
    lg: 'w-12 h-12',
  }

  const iconSizes = {
    sm: 'w-4 h-4',
    md: 'w-5 h-5',
    lg: 'w-6 h-6',
  }

  return (
    <div
      className={clsx(
        'rounded-full bg-cream flex items-center justify-center flex-shrink-0',
        sizes[size],
        className
      )}
    >
      <Bot className={clsx('text-gold', iconSizes[size])} />
    </div>
  )
}
