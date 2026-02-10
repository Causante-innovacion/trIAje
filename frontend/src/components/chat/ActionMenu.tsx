import { useState, useRef, useEffect } from 'react'
import { Plus, BarChart2, ClipboardCheck, Users } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { useChatStore } from '../../stores/chatStore'
import clsx from 'clsx'

export function ActionMenu() {
    const [isOpen, setIsOpen] = useState(false)
    const menuRef = useRef<HTMLDivElement>(null)
    const navigate = useNavigate()
    const { startTool } = useChatStore()

    useEffect(() => {
        function handleClickOutside(event: MouseEvent) {
            if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
                setIsOpen(false)
            }
        }
        document.addEventListener('mousedown', handleClickOutside)
        return () => document.removeEventListener('mousedown', handleClickOutside)
    }, [])

    const handleAction = (tool: 'evaluation' | 'compliance' | 'advisor') => {
        startTool(tool)
        navigate(`/chat/${tool}`)
        setIsOpen(false)
    }

    return (
        <div className="relative" ref={menuRef}>
            <button
                type="button"
                onClick={() => setIsOpen(!isOpen)}
                className={clsx(
                    "w-10 h-10 rounded-full flex items-center justify-center transition-all duration-200",
                    isOpen
                        ? "bg-gray-900 text-yellow-400 rotate-45"
                        : "text-gray-400 hover:text-gray-600 hover:bg-gray-100"
                )}
            >
                <Plus className="w-6 h-6" />
            </button>

            {isOpen && (
                <div className="absolute bottom-14 left-0 w-72 bg-gray-900 rounded-xl shadow-xl p-2 z-50 animate-in fade-in slide-in-from-bottom-4 duration-200">
                    <div className="space-y-1">
                        <button
                            onClick={() => handleAction('evaluation')}
                            className="w-full flex items-center gap-4 p-3 rounded-lg hover:bg-gray-800 transition-colors group text-left"
                        >
                            <div className="w-10 h-10 rounded-lg bg-yellow-900/30 flex items-center justify-center text-yellow-500 group-hover:bg-yellow-900/50 group-hover:text-yellow-400 transition-colors">
                                <BarChart2 className="w-5 h-5" />
                            </div>
                            <span className="text-gray-200 font-medium group-hover:text-white">
                                Evaluar proyecto
                            </span>
                        </button>

                        <button
                            onClick={() => handleAction('compliance')}
                            className="w-full flex items-center gap-4 p-3 rounded-lg hover:bg-gray-800 transition-colors group text-left"
                        >
                            <div className="w-10 h-10 rounded-lg bg-yellow-900/30 flex items-center justify-center text-yellow-500 group-hover:bg-yellow-900/50 group-hover:text-yellow-400 transition-colors">
                                <ClipboardCheck className="w-5 h-5" />
                            </div>
                            <span className="text-gray-200 font-medium group-hover:text-white">
                                Ruta de cumplimiento
                            </span>
                        </button>

                        <button
                            onClick={() => handleAction('advisor')}
                            className="w-full flex items-center gap-4 p-3 rounded-lg hover:bg-gray-800 transition-colors group text-left"
                        >
                            <div className="w-10 h-10 rounded-lg bg-yellow-900/30 flex items-center justify-center text-yellow-500 group-hover:bg-yellow-900/50 group-hover:text-yellow-400 transition-colors">
                                <Users className="w-5 h-5" />
                            </div>
                            <span className="text-gray-200 font-medium group-hover:text-white">
                                Preparar reunión
                            </span>
                        </button>
                    </div>
                </div>
            )}
        </div>
    )
}
