import { useState, useRef, useEffect } from 'react'
import { Plus, FileUp } from 'lucide-react'
import clsx from 'clsx'

interface ActionMenuProps {
    onFileSelect?: (file: File) => void
}

export function ActionMenu({ onFileSelect }: ActionMenuProps) {
    const [isOpen, setIsOpen] = useState(false)
    const menuRef = useRef<HTMLDivElement>(null)
    const fileInputRef = useRef<HTMLInputElement>(null)

    useEffect(() => {
        function handleClickOutside(event: MouseEvent) {
            if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
                setIsOpen(false)
            }
        }
        document.addEventListener('mousedown', handleClickOutside)
        return () => document.removeEventListener('mousedown', handleClickOutside)
    }, [])

    const handleUploadClick = () => {
        fileInputRef.current?.click()
        setIsOpen(false)
    }

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const files = e.target.files
        if (files && files.length > 0 && onFileSelect) {
            onFileSelect(files[0])
        }
        // Reset input so the same file can be selected again
        if (fileInputRef.current) {
            fileInputRef.current.value = ''
        }
    }

    return (
        <div className="relative" ref={menuRef}>
            <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.docx,.txt"
                onChange={handleFileChange}
                className="hidden"
            />
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
                <div className="absolute bottom-14 left-0 w-64 bg-gray-900 rounded-xl shadow-xl p-2 z-50 animate-in fade-in slide-in-from-bottom-4 duration-200">
                    <div className="space-y-1">
                        <button
                            onClick={handleUploadClick}
                            className="w-full flex items-center gap-4 p-3 rounded-lg hover:bg-gray-800 transition-colors group text-left"
                        >
                            <div className="w-10 h-10 rounded-lg bg-yellow-900/30 flex items-center justify-center text-yellow-500 group-hover:bg-yellow-900/50 group-hover:text-yellow-400 transition-colors">
                                <FileUp className="w-5 h-5" />
                            </div>
                            <div>
                                <span className="text-gray-200 font-medium group-hover:text-white block">
                                    Subir archivo
                                </span>
                                <span className="text-gray-500 text-xs">
                                    PDF, DOCX, TXT — máx. 10 MB
                                </span>
                            </div>
                        </button>
                    </div>
                </div>
            )}
        </div>
    )
}

