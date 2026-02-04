import { Check, X } from 'lucide-react'
import { MessageOption } from '../../types/chat'

interface OptionButtonsProps {
  options: MessageOption[]
  onSelect?: (value: string) => void
  disabled?: boolean
}

export function OptionButtons({ options, onSelect, disabled }: OptionButtonsProps) {
  const handleClick = (value: string) => {
    if (!disabled && onSelect) {
      onSelect(value)
    }
  }

  return (
    <div className="flex flex-wrap gap-3 mt-4">
      {options.map((option) => {
        const isYes = option.icon === 'check' || option.value === 'yes'

        return (
          <button
            key={option.id}
            onClick={() => handleClick(option.value)}
            disabled={disabled}
            className={
              isYes
                ? 'btn-option-yes disabled:opacity-50 disabled:cursor-not-allowed'
                : 'btn-option-no disabled:opacity-50 disabled:cursor-not-allowed'
            }
          >
            {isYes ? (
              <Check className="w-4 h-4 text-green-400" />
            ) : (
              <X className="w-4 h-4 text-red-400" />
            )}
            {option.label}
          </button>
        )
      })}
    </div>
  )
}
