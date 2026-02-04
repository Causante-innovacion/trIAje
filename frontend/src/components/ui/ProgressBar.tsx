import clsx from 'clsx'

interface ProgressBarProps {
  progress: number
  showPercentage?: boolean
  size?: 'sm' | 'md' | 'lg'
  className?: string
}

export function ProgressBar({
  progress,
  showPercentage = false,
  size = 'md',
  className,
}: ProgressBarProps) {
  const clampedProgress = Math.min(100, Math.max(0, progress))

  const sizes = {
    sm: 'h-1',
    md: 'h-2',
    lg: 'h-3',
  }

  return (
    <div className={clsx('w-full', className)}>
      <div className={clsx('bg-gray-200 rounded-full overflow-hidden', sizes[size])}>
        <div
          className="h-full bg-viable rounded-full transition-all duration-300 ease-out"
          style={{ width: `${clampedProgress}%` }}
        />
      </div>
      {showPercentage && (
        <span className="text-sm text-gray-500 mt-1 block text-right">
          {Math.round(clampedProgress)}%
        </span>
      )}
    </div>
  )
}
