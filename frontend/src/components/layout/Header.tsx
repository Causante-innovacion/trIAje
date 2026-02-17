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
          ? "bg-white border-b border-gray-200"
          : "bg-white border-b border-transparent"
      )}
    >
      <div className="max-w-7xl mx-auto px-6 flex items-center justify-between">
        {/* Logo + Title */}
        <div className="flex items-center gap-3">
          <Link
            to="/"
            onClick={handleLogoClick}
            className="flex items-center gap-3 hover:opacity-75 transition-opacity cursor-pointer"
          >
            <img
              src="https://causante.org/wp-content/uploads/2025/03/causante-logo.webp"
              alt="CAUSANTE"
              className="h-7 w-auto"
            />
            <div className="hidden sm:flex items-center gap-2">
              <span className="w-px h-5 bg-gray-200" />
              <span className="font-heading text-sm font-bold tracking-wide text-gray-900 uppercase">
                GPT Legal
              </span>
            </div>
          </Link>
        </div>

        {/* Dynamic Right Content */}
        <div className="flex items-center gap-4">
          {rightContent}
        </div>
      </div>
    </header>
  )
}
