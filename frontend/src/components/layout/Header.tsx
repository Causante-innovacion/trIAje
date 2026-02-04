import { Link } from 'react-router-dom'
import { useChatStore } from '../../stores/chatStore'

export function Header() {
  const { resetToHome, currentTool } = useChatStore()

  const handleLogoClick = () => {
    if (currentTool) {
      resetToHome()
    }
  }

  return (
    <header className="fixed top-0 left-0 z-50 p-4 md:p-6">
      <Link
        to="/"
        onClick={handleLogoClick}
        className="flex items-center gap-3 hover:opacity-80 transition-opacity"
      >
        <img
          src="https://causante.org/wp-content/uploads/2025/03/causante-logo.webp"
          alt="GPT Legal Logo"
          className="h-8 w-auto"
        />
        <span className="text-lg font-semibold text-gray-900">GPT Legal</span>
      </Link>
    </header>
  )
}
