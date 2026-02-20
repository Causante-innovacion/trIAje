import { Check, X } from 'lucide-react'
import clsx from 'clsx'

// ─── Causante Design Tokens ───
const SELECTED = 'border-2 border-causante-ocre bg-gold-50 text-gray-900 font-semibold'
const UNSELECTED = 'border border-gray-200 hover:border-causante-ocre/40 hover:bg-gold-50/50'
const DISABLED = 'opacity-50 cursor-not-allowed hover:bg-transparent hover:border-gray-200'
const BASE_CHIP = 'rounded-full text-sm transition-all duration-200 flex items-center justify-center p-3 text-center'

// Yes/No Button Group
interface YesNoButtonsProps {
  value: boolean | null
  onChange: (value: boolean) => void
  yesLabel?: string
  noLabel?: string
  threeOptions?: boolean
  thirdLabel?: string
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
          `${BASE_CHIP} min-h-[52px] px-6`,
          value === true ? SELECTED : UNSELECTED,
          disabled && DISABLED
        )}
      >
        <Check className={clsx('w-4 h-4 mr-2', value === true ? 'text-green-600' : 'text-gray-400')} />
        {yesLabel}
      </button>
      <button
        type="button"
        onClick={() => !disabled && onChange(false)}
        disabled={disabled}
        className={clsx(
          `${BASE_CHIP} min-h-[52px] px-6`,
          value === false ? SELECTED : UNSELECTED,
          disabled && DISABLED
        )}
      >
        <X className={clsx('w-4 h-4 mr-2', value === false ? 'text-red-500' : 'text-gray-400')} />
        {noLabel}
      </button>
      {threeOptions && (
        <button
          type="button"
          onClick={() => !disabled && onChange(null as unknown as boolean)}
          disabled={disabled}
          className={clsx(
            `${BASE_CHIP} min-h-[52px] px-6`,
            value === null ? SELECTED : UNSELECTED,
            disabled && DISABLED
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
    2: 'grid-cols-1 sm:grid-cols-2',
    3: 'grid-cols-1 sm:grid-cols-2 md:grid-cols-3',
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
            `${BASE_CHIP} min-h-[52px] px-4`,
            value === option ? SELECTED : UNSELECTED,
            disabled && DISABLED
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
    <div className="flex flex-wrap gap-3">
      {options.map((option) => {
        const isSelected = value.includes(option)
        return (
          <button
            key={option}
            type="button"
            onClick={() => toggleOption(option)}
            disabled={disabled}
            className={clsx(
              `${BASE_CHIP} min-w-[120px] min-h-[48px] px-5`,
              isSelected ? SELECTED : UNSELECTED,
              disabled && DISABLED
            )}
          >
            {isSelected && <Check className="w-3.5 h-3.5 mr-1.5 text-causante-ocre" />}
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
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
      {options.map((option) => {
        const isSelected = value.includes(option)
        return (
          <label
            key={option}
            className={clsx(
              'flex items-center gap-3 p-3 rounded-full cursor-pointer transition-all min-h-[48px] px-5',
              isSelected ? SELECTED : UNSELECTED,
              disabled && 'opacity-50 cursor-not-allowed hover:bg-transparent'
            )}
          >
            <input
              type="checkbox"
              checked={isSelected}
              onChange={() => toggleOption(option)}
              disabled={disabled}
              className="rounded text-causante-ocre focus:ring-causante-ocre"
            />
            <span className={clsx('text-sm', isSelected ? 'text-gray-900 font-medium' : '')}>{option}</span>
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
          'px-6 py-2 rounded-full text-xs font-medium flex items-center gap-1 transition-all',
          value === true ? SELECTED : UNSELECTED,
          disabled && DISABLED
        )}
      >
        <Check className={clsx('w-3 h-3', value === true ? 'text-green-600' : 'text-gray-400')} />
        Sí
      </button>
      <button
        type="button"
        onClick={() => !disabled && onChange(false)}
        disabled={disabled}
        className={clsx(
          'px-6 py-2 rounded-full text-xs font-medium flex items-center gap-1 transition-all',
          value === false ? SELECTED : UNSELECTED,
          disabled && DISABLED
        )}
      >
        <X className={clsx('w-3 h-3', value === false ? 'text-red-500' : 'text-gray-400')} />
        No
      </button>
    </div>
  )
}
