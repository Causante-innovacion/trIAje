import { Check, X } from 'lucide-react'
import clsx from 'clsx'

// ─── Causante Design Tokens ───
const SELECTED = 'border-2 border-causante-ocre bg-causante-crema/20 text-gray-900 font-bold shadow-[0_8px_20px_-6px_rgba(179,153,76,0.25)] ring-1 ring-causante-ocre/10'
const UNSELECTED = 'border border-gray-100 bg-white text-gray-600 hover:border-causante-ocre/40 hover:bg-causante-crema/5 hover:shadow-md hover:-translate-y-0.5 shadow-sm'
const DISABLED = 'opacity-50 cursor-not-allowed hover:bg-transparent hover:border-gray-100 hover:shadow-none hover:translate-y-0'
const BASE_CHIP = 'rounded-2xl text-[13px] transition-all duration-300 flex items-center justify-center p-3 text-center leading-tight'

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
    <div className={clsx('grid gap-4', threeOptions ? 'grid-cols-3' : 'grid-cols-2')}>
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
        <Check className={clsx('w-5 h-5 mr-2', value === true ? 'text-causante-ocre' : 'text-gray-300')} />
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
        <X className={clsx('w-5 h-5 mr-2', value === false ? 'text-red-400' : 'text-gray-300')} />
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
  columns?: 1 | 2 | 3 | 4
  disabled?: boolean
}

export function SingleSelect({ options, value, onChange, columns = 1, disabled = false }: SingleSelectProps) {
  const gridClass = {
    1: 'grid-cols-1',
    2: 'grid-cols-1 sm:grid-cols-2',
    3: 'grid-cols-1 sm:grid-cols-2 md:grid-cols-3',
    4: 'grid-cols-2 md:grid-cols-4',
  }

  return (
    <div className={clsx('grid gap-4', gridClass[columns])}>
      {options.map((option) => (
        <button
          key={option}
          type="button"
          onClick={() => !disabled && onChange(option)}
          disabled={disabled}
          className={clsx(
            `${BASE_CHIP} min-h-[60px] px-5 text-left justify-start relative overflow-hidden`,
            value === option ? SELECTED : UNSELECTED,
            disabled && DISABLED
          )}
        >
          {value === option && (
            <div className="absolute left-0 top-0 bottom-0 w-1 bg-causante-ocre" />
          )}
          <span className="flex-1 font-medium">{option}</span>
          {value === option && (
            <div className="flex items-center justify-center w-6 h-6 rounded-full bg-causante-ocre text-white ml-2 shadow-sm">
              <Check className="w-4 h-4" />
            </div>
          )}
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
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
      {options.map((option) => {
        const isSelected = value.includes(option)
        return (
          <button
            key={option}
            type="button"
            onClick={() => toggleOption(option)}
            disabled={disabled}
            className={clsx(
              `${BASE_CHIP} min-h-[48px] px-5`,
              isSelected ? SELECTED : UNSELECTED,
              disabled && DISABLED
            )}
          >
            {isSelected && <Check className="w-4 h-4 mr-2 text-causante-ocre" />}
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
