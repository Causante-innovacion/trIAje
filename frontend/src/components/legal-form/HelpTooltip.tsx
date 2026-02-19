import { useState, useRef, useEffect } from 'react'
import { Lightbulb, X } from 'lucide-react'

interface HelpTooltipProps {
  text: string
}

export function HelpTooltip({ text }: HelpTooltipProps) {
  const [isOpen, setIsOpen] = useState(false)
  const tooltipRef = useRef<HTMLDivElement>(null)
  const iconRef = useRef<HTMLButtonElement>(null)

  // Close on click outside
  useEffect(() => {
    if (!isOpen) return

    const handleClickOutside = (e: MouseEvent) => {
      if (
        tooltipRef.current && !tooltipRef.current.contains(e.target as Node) &&
        iconRef.current && !iconRef.current.contains(e.target as Node)
      ) {
        setIsOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [isOpen])

  // Adjust position to stay within viewport
  useEffect(() => {
    if (!isOpen || !tooltipRef.current) return

    const tooltip = tooltipRef.current
    const rect = tooltip.getBoundingClientRect()

    // If tooltip goes off the right edge, shift it left
    if (rect.right > window.innerWidth - 16) {
      tooltip.style.right = '0'
      tooltip.style.left = 'auto'
    }

    // If tooltip goes off the left edge, shift it right
    if (rect.left < 16) {
      tooltip.style.left = '0'
      tooltip.style.right = 'auto'
    }
  }, [isOpen])

  return (
    <div className="relative flex-shrink-0">
      <button
        ref={iconRef}
        type="button"
        onMouseEnter={() => setIsOpen(true)}
        onMouseLeave={() => setIsOpen(false)}
        onClick={() => setIsOpen(!isOpen)}
        className="p-1 rounded-full hover:bg-yellow-100 transition-colors focus:outline-none"
        aria-label="Ayuda"
      >
        <Lightbulb className="w-4 h-4 text-yellow-400" />
      </button>

      {isOpen && (
        <div
          ref={tooltipRef}
          className="absolute z-50 right-0 top-full mt-2 w-80 max-w-[90vw] max-h-80 overflow-y-auto bg-white border border-yellow-200 rounded-xl shadow-lg p-4 animate-fade-in"
          onMouseEnter={() => setIsOpen(true)}
          onMouseLeave={() => setIsOpen(false)}
        >
          {/* Arrow */}
          <div className="absolute -top-2 right-3 w-4 h-4 bg-white border-l border-t border-yellow-200 transform rotate-45" />

          {/* Close button for mobile */}
          <button
            type="button"
            onClick={() => setIsOpen(false)}
            className="absolute top-2 right-2 p-1 rounded-full hover:bg-gray-100 md:hidden"
          >
            <X className="w-3 h-3 text-gray-400" />
          </button>

          {/* Content */}
          {/* Content */}
          <div className="relative text-xs text-gray-600 leading-relaxed space-y-2">
            {text.split('\n').filter(line => line.trim() !== '').map((line, i) => (
              <p key={i}>
                {line.split(/(\*\*.*?\*\*)/g).map((part, j) => {
                  if (part.startsWith('**') && part.endsWith('**')) {
                    return <strong key={j} className="font-semibold text-gray-800">{part.slice(2, -2)}</strong>
                  }
                  return part
                })}
              </p>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
