import { useRef, useState, useEffect } from 'react'
import { Check, Circle, LucideIcon, ChevronLeft, ChevronRight } from 'lucide-react'
import clsx from 'clsx'

interface Block {
  id: string
  name: string
  icon: LucideIcon
  color: string
  completed: number
  total: number
}

interface ProgressTrackerProps {
  completedQuestions: number
  totalQuestions: number
  blocks: Block[]
  isFinished?: boolean
}

const colorStyles: Record<string, string> = {
  blue: 'bg-yellow-100 text-yellow-700 border-yellow-300',
  purple: 'bg-yellow-100 text-yellow-700 border-yellow-300',
  green: 'bg-yellow-100 text-yellow-700 border-yellow-300',
  orange: 'bg-yellow-100 text-yellow-700 border-yellow-300',
  teal: 'bg-yellow-100 text-yellow-700 border-yellow-300',
  indigo: 'bg-yellow-100 text-yellow-700 border-yellow-300',
  pink: 'bg-yellow-100 text-yellow-700 border-yellow-300',
}

export function ProgressTracker({ completedQuestions, totalQuestions, blocks, isFinished = false }: ProgressTrackerProps) {
  let progressPercentage = Math.round((completedQuestions / totalQuestions) * 100)

  // Cap at 99% if 100% completed but not marked as finished
  if (progressPercentage === 100 && !isFinished) {
    progressPercentage = 99
  }
  const scrollRef = useRef<HTMLDivElement>(null)
  const [scrollProgress, setScrollProgress] = useState(0)
  const [canScrollLeft, setCanScrollLeft] = useState(false)
  const [canScrollRight, setCanScrollRight] = useState(true)

  const updateScrollState = () => {
    if (scrollRef.current) {
      const { scrollLeft, scrollWidth, clientWidth } = scrollRef.current
      const maxScroll = scrollWidth - clientWidth
      setScrollProgress(maxScroll > 0 ? scrollLeft / maxScroll : 0)
      setCanScrollLeft(scrollLeft > 0)
      setCanScrollRight(scrollLeft < maxScroll - 1)
    }
  }

  useEffect(() => {
    updateScrollState()
    const ref = scrollRef.current
    if (ref) {
      ref.addEventListener('scroll', updateScrollState)
      return () => ref.removeEventListener('scroll', updateScrollState)
    }
  }, [])

  const scroll = (direction: 'left' | 'right') => {
    if (scrollRef.current) {
      const scrollAmount = 200
      scrollRef.current.scrollBy({
        left: direction === 'left' ? -scrollAmount : scrollAmount,
        behavior: 'smooth',
      })
    }
  }

  return (
    <div className="bg-white border border-gray-100 rounded-2xl p-6 mb-8 shadow-sm">
      <div className="flex justify-between items-start mb-6">
        <div>
          <h2 className="text-lg font-bold">Progreso Global de Cumplimiento</h2>
          <p className="text-xs text-gray-400">Completa los {blocks.length} bloques para generar tu reporte final.</p>
        </div>
        <div className="text-right">
          <span className="text-2xl font-bold text-gold">
            {completedQuestions}
            <span className="text-gray-300">/{totalQuestions}</span>
          </span>
          <p className="text-[10px] text-gray-400 uppercase font-bold">Preguntas completadas</p>
        </div>
      </div>

      {/* Progress bar */}
      <div className="w-full bg-gray-100 h-2 rounded-full mb-6">
        <div
          className="h-full rounded-full transition-all duration-500"
          style={{ width: `${progressPercentage}%`, backgroundColor: '#D7D100' }}
        />
      </div>

      {/* Block indicators - horizontal scroll */}
      <div className="relative">
        {/* Scroll buttons */}
        {canScrollLeft && (
          <button
            onClick={() => scroll('left')}
            className="absolute left-0 top-1/2 -translate-y-1/2 z-10 w-8 h-8 bg-white shadow-md rounded-full flex items-center justify-center hover:bg-gray-50"
          >
            <ChevronLeft className="w-4 h-4 text-gray-600" />
          </button>
        )}
        {canScrollRight && (
          <button
            onClick={() => scroll('right')}
            className="absolute right-0 top-1/2 -translate-y-1/2 z-10 w-8 h-8 bg-white shadow-md rounded-full flex items-center justify-center hover:bg-gray-50"
          >
            <ChevronRight className="w-4 h-4 text-gray-600" />
          </button>
        )}

        {/* Scrollable container */}
        <div
          ref={scrollRef}
          className="flex gap-3 overflow-x-auto scrollbar-hide pb-2 px-1"
          style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}
        >
          {blocks.map((block) => {
            const isComplete = block.completed === block.total
            const hasProgress = block.completed > 0
            const BlockIcon = isComplete ? Check : Circle
            const percentage = Math.round((block.completed / block.total) * 100)

            return (
              <div
                key={block.id}
                className={clsx(
                  'flex-shrink-0 p-3 rounded-lg border flex items-center gap-2 min-w-[140px]',
                  isComplete
                    ? colorStyles[block.color]
                    : hasProgress
                      ? 'bg-yellow-50 border-yellow-200'
                      : 'bg-gray-50 border-gray-100'
                )}
              >
                <BlockIcon
                  className={clsx(
                    'w-4 h-4',
                    isComplete ? 'text-yellow-600' : hasProgress ? 'text-yellow-500' : 'text-gray-400'
                  )}
                />
                <div>
                  <p
                    className={clsx(
                      'text-[10px] font-bold uppercase whitespace-nowrap',
                      isComplete ? 'text-yellow-700' : hasProgress ? 'text-yellow-600' : 'text-gray-400'
                    )}
                  >
                    {block.name}
                  </p>
                  <p
                    className={clsx(
                      'text-[10px]',
                      isComplete ? 'text-yellow-600' : hasProgress ? 'text-yellow-500' : 'text-gray-400'
                    )}
                  >
                    {percentage}%
                  </p>
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Scroll progress indicator */}
      <div className="mt-4 h-1 bg-gray-100 rounded-full overflow-hidden relative">
        <div
          className="absolute top-0 left-0 h-full bg-blue-500 rounded-full transition-all duration-150"
          style={{
            width: '30%',
            transform: `translateX(${scrollProgress * 233}%)`,
          }}
        />
      </div>
    </div>
  )
}
