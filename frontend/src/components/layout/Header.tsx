import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useChatStore } from '../../stores/chatStore'
import { useHeaderStore } from '../../stores/headerStore'
import clsx from 'clsx'

export function Header() {
  const { resetToHome, currentTool } = useChatStore()
  const { rightContent } = useHeaderStore()
  const [isScrolled, setIsScrolled] = useState(false)

  const handleLogoClick = () => {
    if (currentTool) {
      resetToHome()
    }
  }

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
          ? "bg-white/90 backdrop-blur-md border-b border-gray-200 shadow-sm"
          : "bg-white border-b border-transparent"
      )}
    >
      <div className="max-w-7xl mx-auto px-4 flex items-center justify-between">
        {/* Logo + Title "Aplicaciones" */}
        <div className="flex items-center gap-3">
          <Link
            to="/"
            onClick={handleLogoClick}
            className="flex items-center gap-3 hover:opacity-75 transition-opacity cursor-pointer"
          >
            <img
              src="https://causante.org/wp-content/uploads/2025/03/causante-logo.webp"
              alt="CAUSANTE"
              className="h-8 w-auto"
            />
            {/* Added GPT Legal text as per previous design, can remove if user insists on exact code */}
            <span className="text-lg font-semibold text-gray-900 hidden sm:block">GPT Legal</span>
          </Link>

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
