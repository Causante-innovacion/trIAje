import { Link } from 'react-router-dom'

export function Footer() {
  return (
    <footer className="fixed bottom-0 left-0 right-0 py-3 text-center bg-white/80 z-10 backdrop-blur-sm border-t border-gray-100/50">
      <p className="text-[11px] text-gray-400 tracking-wide flex items-center justify-center gap-2">
        <span>IA entrenada en normativa civil y administrativa peruana · <span className="font-medium text-gray-500">CAUSANTE</span></span>
        <span className="text-gray-300">|</span>
        <Link to="/privacy" className="hover:text-amber-600 transition-colors">
          Políticas de Privacidad
        </Link>
      </p>
    </footer>
  )
}
