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
}

export function YesNoButtons({
  value,
  onChange,
  yesLabel = 'Sí',
  noLabel = 'No',
  threeOptions = false,
  thirdLabel = 'En trámite',
}: YesNoButtonsProps) {
  return (
    <div className={clsx(threeOptions ? 'flex justify-between w-full' : 'grid grid-cols-2 gap-3')}>
      <button
        type="button"
        onClick={() => onChange(true)}
        className={clsx(
          'py-3 rounded-xl text-sm font-medium flex items-center justify-center gap-2 transition-all',
          value === true
            ? 'border-2 border-yellow-400 bg-yellow-50 text-yellow-800'
            : 'border border-gray-200 hover:border-yellow-300 hover:bg-yellow-50',
          threeOptions && 'w-[201px] h-[73px] text-xs'
        )}
      >
        <Check className={clsx('w-4 h-4', value === true ? 'text-green-500' : 'text-gray-400')} />
        {yesLabel}
      </button>
      <button
        type="button"
        onClick={() => onChange(false)}
        className={clsx(
          'py-3 rounded-xl text-sm font-medium flex items-center justify-center gap-2 transition-all',
          value === false
            ? 'border-2 border-yellow-400 bg-yellow-50 text-yellow-800'
            : 'border border-gray-200 hover:border-gray-300 hover:bg-gray-50',
          threeOptions && 'w-[201px] h-[73px] text-xs'
        )}
      >
        <X className={clsx('w-4 h-4', value === false ? 'text-red-400' : 'text-gray-400')} />
        {noLabel}
      </button>
      {threeOptions && (
        <button
          type="button"
          onClick={() => onChange(null as unknown as boolean)}
          className={clsx(
            'py-3 rounded-xl text-sm font-medium flex items-center justify-center gap-2 transition-all',
            value === null
              ? 'border-2 border-yellow-400 bg-yellow-50 text-yellow-800'
              : 'border border-gray-200 hover:border-gray-300 hover:bg-yellow-50',
            threeOptions && 'w-[201px] h-[73px] text-xs'
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
}

export function SingleSelect({ options, value, onChange, columns = 3 }: SingleSelectProps) {
  const isThreeOrLess = options.length <= 3 && columns <= 3

  const gridClass = {
    2: 'grid-cols-2',
    3: 'grid-cols-2 md:grid-cols-3',
    4: 'grid-cols-2 md:grid-cols-4',
  }

  const isExactlyThree = options.length === 3 && columns === 3

  if (isExactlyThree) {
    return (
      <div className="flex justify-between w-full">
        {options.map((option) => (
          <button
            key={option}
            type="button"
            onClick={() => onChange(option)}
            className={clsx(
              'rounded-xl font-medium transition-all text-center flex items-center justify-center p-2',
              value === option
                ? 'border-2 border-yellow-400 bg-yellow-50 text-yellow-800'
                : 'border border-gray-200 hover:border-yellow-300 hover:bg-yellow-50',
              'w-[201px] h-[73px] text-xs'
            )}
          >
            {option}
          </button>
        ))}
      </div>
    )
  }

  return (
    <div className={clsx('grid gap-3', gridClass[columns])}>
      {options.map((option) => (
        <button
          key={option}
          type="button"
          onClick={() => onChange(option)}
          className={clsx(
            'rounded-xl font-medium transition-all text-center flex items-center justify-center p-2',
            value === option
              ? 'border-2 border-yellow-400 bg-yellow-50 text-yellow-800'
              : 'border border-gray-200 hover:border-yellow-300 hover:bg-yellow-50',
            isThreeOrLess ? 'w-[201px] h-[73px] text-xs' : 'w-[151px] h-[55px] text-[10px]'
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
}

export function MultiSelectChips({ options, value, onChange }: MultiSelectChipsProps) {
  const toggleOption = (option: string) => {
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
            className={clsx(
              'rounded-xl text-[10px] font-medium transition-all flex items-center justify-center p-2 text-center w-[151px] h-[55px]',
              isSelected
                ? 'border-2 border-yellow-400 bg-yellow-50 text-yellow-800'
                : 'border border-gray-200 hover:border-yellow-300 hover:bg-yellow-50'
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
}

export function MultiSelectCheckbox({ options, value, onChange }: MultiSelectCheckboxProps) {
  const toggleOption = (option: string) => {
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
              'flex items-center gap-3 p-3 rounded-xl cursor-pointer transition-all',
              isSelected
                ? 'border-2 border-yellow-400 bg-yellow-50'
                : 'border border-gray-100 hover:bg-gray-50'
            )}
          >
            <input
              type="checkbox"
              checked={isSelected}
              onChange={() => toggleOption(option)}
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
}

export function InlineYesNo({ value, onChange }: InlineYesNoProps) {
  return (
    <div className="flex gap-2">
      <button
        type="button"
        onClick={() => onChange(true)}
        className={clsx(
          'px-6 py-2 rounded-lg text-xs font-medium flex items-center gap-1 transition-all',
          value === true
            ? 'border-2 border-yellow-400 bg-yellow-50 text-yellow-800'
            : 'border border-gray-200 hover:border-yellow-300'
        )}
      >
        <Check className={clsx('w-3 h-3', value === true ? 'text-green-500' : 'text-gray-400')} />
        Sí
      </button>
      <button
        type="button"
        onClick={() => onChange(false)}
        className={clsx(
          'px-6 py-2 rounded-lg text-xs font-medium flex items-center gap-1 transition-all',
          value === false
            ? 'border-2 border-yellow-400 bg-yellow-50 text-yellow-800'
            : 'border border-gray-200 hover:border-gray-300'
        )}
      >
        <X className={clsx('w-3 h-3', value === false ? 'text-red-400' : 'text-gray-400')} />
        No
      </button>
    </div>
  )
}
