import { useState, useEffect } from 'react'
import { useHeaderStore } from '../../stores/headerStore'
import clsx from 'clsx'

export function Header() {
  const { rightContent } = useHeaderStore()
  const [isScrolled, setIsScrolled] = useState(false)

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 20)
    }

    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  return (
    <header
      className={clsx(
        "py-3 print:hidden sticky top-0 z-40 transition-all duration-300",
        isScrolled
          ? "bg-white/90 backdrop-blur-md border-b border-primary-200 shadow-sm"
          : "bg-white border-b border-transparent"
      )}
    >
      <div className="max-w-7xl mx-auto px-4 flex items-center justify-between">
        {/* Logo + Título "Aplicaciones" */}
        <div className="flex items-center gap-3">
          <a
            href="https://apps.causante.org/"
            className="flex items-center gap-3 hover:opacity-75 transition-opacity cursor-pointer"
          >
            <img
              src="https://causante.org/wp-content/uploads/2025/03/causante-logo.webp"
              alt="CAUSANTE"
              className="h-8 w-auto"
            />
          </a>

          {/* Separador y Texto "APLICACIONES" */}
          <div className="hidden md:flex items-center gap-2">
            <span className="text-gray-300 font-light">|</span>
            <span className="text-sm font-bold text-gray-600 uppercase tracking-wider">
              Aplicaciones
            </span>
          </div>
        </div>

        {/* Dynamic Right Content */}
        <div className="flex items-center gap-4">
          {rightContent}
        </div>
      </div>
    </header>
  )
}
