import { useState, useRef, useCallback } from 'react'
import { FileUp, FolderOpen, Lightbulb } from 'lucide-react'
import clsx from 'clsx'

interface FileUploadProps {
  onFileSelect?: (file: File) => void
  accept?: string
  maxSize?: number // in MB
}

export function FileUpload({
  onFileSelect,
  accept = '.pdf,.docx,.txt',
  maxSize = 10,
}: FileUploadProps) {
  const [isDragging, setIsDragging] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const validateFile = (file: File): boolean => {
    setError(null)

    // Check file type
    const allowedTypes = [
      'application/pdf',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'text/plain',
      '',
    ]
    const ext = file.name.split('.').pop()?.toLowerCase() ?? ''
    const allowedExts = ['pdf', 'docx', 'txt']
    if (!allowedTypes.includes(file.type) && !allowedExts.includes(ext)) {
      setError('Solo se permiten archivos PDF, DOCX o TXT')
      return false
    }

    // Check file size
    const fileSizeInMB = file.size / 1024 / 1024
    if (fileSizeInMB > maxSize) {
      setError(`El archivo no debe superar ${maxSize} MB`)
      return false
    }

    return true
  }

  const handleFile = useCallback((file: File) => {
    if (validateFile(file) && onFileSelect) {
      onFileSelect(file)
    }
  }, [onFileSelect, maxSize])

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)

    const files = e.dataTransfer.files
    if (files.length > 0) {
      handleFile(files[0])
    }
  }, [handleFile])

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (files && files.length > 0) {
      handleFile(files[0])
    }
  }

  const handleClick = () => {
    inputRef.current?.click()
  }

  return (
    <div className="space-y-4">
      <div
        className={clsx(
          'file-upload-zone',
          isDragging && 'dragging border-gold bg-gold-50'
        )}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={handleClick}
      >
        <input
          ref={inputRef}
          type="file"
          accept={accept}
          onChange={handleInputChange}
          className="hidden"
        />

        <div className="flex flex-col items-center gap-3">
          <div className="w-12 h-12 bg-cream rounded-xl flex items-center justify-center">
            <FileUp className="w-6 h-6 text-gold" />
          </div>

          <div>
            <p className="font-medium text-gray-900">
              Arrastra tu archivo aquí
            </p>
            <p className="text-sm text-gray-400">
              (PDF, DOCX, TXT - máx. {maxSize} MB)
            </p>
          </div>

          <button
            type="button"
            className="btn-primary flex items-center gap-2"
            onClick={(e) => {
              e.stopPropagation()
              handleClick()
            }}
          >
            <FolderOpen className="w-4 h-4" />
            Seleccionar archivo
          </button>
        </div>
      </div>

      {error && (
        <p className="text-sm text-red-500 text-center">{error}</p>
      )}

      <div className="flex items-start gap-2 text-sm text-gold">
        <Lightbulb className="w-4 h-4 mt-0.5 flex-shrink-0" />
        <p>
          <strong>Tip:</strong> Asegúrate de tener en orden tu archivo.
        </p>
      </div>
    </div>
  )
}
