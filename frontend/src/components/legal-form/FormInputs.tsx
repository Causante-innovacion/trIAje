import { Check, X } from 'lucide-react'
import clsx from 'clsx'

// Yes/No Button Group
interface YesNoButtonsProps {
  value: boolean | null
  onChange: (value: boolean) => void
  yesLabel?: string
  noLabel?: string
  threeOptions?: boolean
  thirdLabel?: string
  thirdValue?: string
  disabled?: boolean
}

export function YesNoButtons({
  value,
  onChange,
  yesLabel = 'Sí',
  noLabel = 'No',
  threeOptions = false,
  thirdLabel = 'En trámite',
  disabled = false,
}: YesNoButtonsProps) {
  return (
    <div className={clsx('grid gap-3', threeOptions ? 'grid-cols-3' : 'grid-cols-2')}>
      <button
        type="button"
        onClick={() => !disabled && onChange(true)}
        disabled={disabled}
        className={clsx(
          'w-full min-h-[56px] p-3 rounded-xl text-sm font-medium flex items-center justify-center gap-2 transition-all',
          value === true
            ? 'border-2 border-yellow-400 bg-yellow-50 text-yellow-800'
            : 'border border-gray-200 hover:border-yellow-300 hover:bg-yellow-50',
          disabled && 'opacity-50 cursor-not-allowed hover:bg-transparent hover:border-gray-200'
        )}
      >
        <Check className={clsx('w-4 h-4', value === true ? 'text-green-500' : 'text-gray-400')} />
        {yesLabel}
      </button>
      <button
        type="button"
        onClick={() => !disabled && onChange(false)}
        disabled={disabled}
        className={clsx(
          'w-full min-h-[56px] p-3 rounded-xl text-sm font-medium flex items-center justify-center gap-2 transition-all',
          value === false
            ? 'border-2 border-yellow-400 bg-yellow-50 text-yellow-800'
            : 'border border-gray-200 hover:border-gray-300 hover:bg-gray-50',
          disabled && 'opacity-50 cursor-not-allowed hover:bg-transparent hover:border-gray-200'
        )}
      >
        <X className={clsx('w-4 h-4', value === false ? 'text-red-400' : 'text-gray-400')} />
        {noLabel}
      </button>
      {threeOptions && (
        <button
          type="button"
          onClick={() => !disabled && onChange(null as unknown as boolean)}
          disabled={disabled}
          className={clsx(
            'w-full min-h-[56px] p-3 rounded-xl text-sm font-medium flex items-center justify-center gap-2 transition-all',
            value === null
              ? 'border-2 border-yellow-400 bg-yellow-50 text-yellow-800'
              : 'border border-gray-200 hover:border-gray-300 hover:bg-yellow-50',
            disabled && 'opacity-50 cursor-not-allowed hover:bg-transparent hover:border-gray-200'
          )}
        >
          {thirdLabel}
        </button>
      )}
    </div>
  )
}

// Single Select Buttons
interface SingleSelectProps {
  options: string[]
  value: string | null
  onChange: (value: string) => void
  columns?: 2 | 3 | 4
  disabled?: boolean
}

export function SingleSelect({ options, value, onChange, columns = 3, disabled = false }: SingleSelectProps) {
  const gridClass = {
    2: 'grid-cols-2',
    3: 'grid-cols-2 md:grid-cols-3',
    4: 'grid-cols-2 md:grid-cols-4',
  }

  return (
    <div className={clsx('grid gap-3', gridClass[columns])}>
      {options.map((option) => (
        <button
          key={option}
          type="button"
          onClick={() => !disabled && onChange(option)}
          disabled={disabled}
          className={clsx(
            'w-full min-h-[56px] rounded-xl text-sm font-medium transition-all text-center flex items-center justify-center p-3',
            value === option
              ? 'border-2 border-yellow-400 bg-yellow-50 text-yellow-800'
              : 'border border-gray-200 hover:border-yellow-300 hover:bg-yellow-50',
            disabled && 'opacity-50 cursor-not-allowed hover:bg-transparent hover:border-gray-200'
          )}
        >
          {option}
        </button>
      ))}
    </div>
  )
}

// Multi Select Buttons (chips/pills)
interface MultiSelectChipsProps {
  options: string[]
  value: string[]
  onChange: (value: string[]) => void
  disabled?: boolean
}

export function MultiSelectChips({ options, value, onChange, disabled = false }: MultiSelectChipsProps) {
  const toggleOption = (option: string) => {
    if (disabled) return
    if (value.includes(option)) {
      onChange(value.filter((v) => v !== option))
    } else {
      onChange([...value, option])
    }
  }

  return (
    <div className="flex flex-wrap gap-3 justify-center">
      {options.map((option) => {
        const isSelected = value.includes(option)
        return (
          <button
            key={option}
            type="button"
            onClick={() => toggleOption(option)}
            disabled={disabled}
            className={clsx(
              'rounded-xl text-sm font-medium transition-all flex items-center justify-center p-3 text-center min-w-[140px] min-h-[56px]',
              isSelected
                ? 'border-2 border-yellow-400 bg-yellow-50 text-yellow-800'
                : 'border border-gray-200 hover:border-yellow-300 hover:bg-yellow-50',
              disabled && 'opacity-50 cursor-not-allowed hover:bg-transparent hover:border-gray-200'
            )}
          >
            {option}
          </button>
        )
      })}
    </div>
  )
}

// Multi Select Checkboxes
interface MultiSelectCheckboxProps {
  options: string[]
  value: string[]
  onChange: (value: string[]) => void
  disabled?: boolean
}

export function MultiSelectCheckbox({ options, value, onChange, disabled = false }: MultiSelectCheckboxProps) {
  const toggleOption = (option: string) => {
    if (disabled) return
    if (value.includes(option)) {
      onChange(value.filter((v) => v !== option))
    } else {
      onChange([...value, option])
    }
  }

  return (
    <div className="grid grid-cols-2 gap-3">
      {options.map((option) => {
        const isSelected = value.includes(option)
        return (
          <label
            key={option}
            className={clsx(
              'flex items-center gap-3 p-3 rounded-xl cursor-pointer transition-all min-h-[56px]',
              isSelected
                ? 'border-2 border-yellow-400 bg-yellow-50'
                : 'border border-gray-100 hover:bg-gray-50',
              disabled && 'opacity-50 cursor-not-allowed hover:bg-transparent'
            )}
          >
            <input
              type="checkbox"
              checked={isSelected}
              onChange={() => toggleOption(option)}
              disabled={disabled}
              className="rounded text-yellow-400 focus:ring-yellow-400"
            />
            <span className={clsx('text-sm', isSelected ? 'text-yellow-800 font-medium' : '')}>{option}</span>
          </label>
        )
      })}
    </div>
  )
}

// Inline Yes/No for compact questions
interface InlineYesNoProps {
  value: boolean | null
  onChange: (value: boolean) => void
  disabled?: boolean
}

export function InlineYesNo({ value, onChange, disabled = false }: InlineYesNoProps) {
  return (
    <div className="flex gap-2">
      <button
        type="button"
        onClick={() => !disabled && onChange(true)}
        disabled={disabled}
        className={clsx(
          'px-6 py-2 rounded-lg text-xs font-medium flex items-center gap-1 transition-all',
          value === true
            ? 'border-2 border-yellow-400 bg-yellow-50 text-yellow-800'
            : 'border border-gray-200 hover:border-yellow-300',
          disabled && 'opacity-50 cursor-not-allowed hover:bg-transparent hover:border-gray-200'
        )}
      >
        <Check className={clsx('w-3 h-3', value === true ? 'text-green-500' : 'text-gray-400')} />
        Sí
      </button>
      <button
        type="button"
        onClick={() => !disabled && onChange(false)}
        disabled={disabled}
        className={clsx(
          'px-6 py-2 rounded-lg text-xs font-medium flex items-center gap-1 transition-all',
          value === false
            ? 'border-2 border-yellow-400 bg-yellow-50 text-yellow-800'
            : 'border border-gray-200 hover:border-gray-300',
          disabled && 'opacity-50 cursor-not-allowed hover:bg-transparent hover:border-gray-200'
        )}
      >
        <X className={clsx('w-3 h-3', value === false ? 'text-red-400' : 'text-gray-400')} />
        No
      </button>
    </div>
  )
}
