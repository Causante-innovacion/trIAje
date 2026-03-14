import { useState, useCallback } from 'react'
import { chatApi } from '../shared/services/api'
import { useChatStore } from '../stores/chatStore'

interface UseFileUploadOptions {
  maxSize?: number // in MB
  allowedTypes?: string[]
  onSuccess?: (data: Record<string, unknown>) => void
  onError?: (error: string) => void
}

export function useFileUpload(options: UseFileUploadOptions = {}) {
  const {
    maxSize = 10,
    allowedTypes = [
      'application/pdf',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'text/plain',
      '',
    ],
    onSuccess,
    onError,
  } = options

  const [isUploading, setIsUploading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [error, setError] = useState<string | null>(null)

  const { currentTool, setUploadProgress } = useChatStore()

  const validateFile = useCallback((file: File): string | null => {
    const ext = file.name.split('.').pop()?.toLowerCase() ?? ''
    if (!allowedTypes.includes(file.type) && !['pdf', 'docx', 'txt'].includes(ext)) {
      return 'Tipo de archivo no permitido. Solo se aceptan PDF, DOCX o TXT.'
    }

    const fileSizeInMB = file.size / 1024 / 1024
    if (fileSizeInMB > maxSize) {
      return `El archivo excede el tamaño máximo de ${maxSize} MB.`
    }

    return null
  }, [allowedTypes, maxSize])

  const uploadFile = useCallback(async (file: File) => {
    // Validate file
    const validationError = validateFile(file)
    if (validationError) {
      setError(validationError)
      onError?.(validationError)
      return null
    }

    setIsUploading(true)
    setProgress(0)
    setError(null)

    try {
      const response = await chatApi.uploadDocument(
        file,
        currentTool || 'evaluation',
        (progressEvent) => {
          const percentCompleted = progressEvent.total
            ? Math.round((progressEvent.loaded * 100) / progressEvent.total)
            : 0
          setProgress(percentCompleted)
          setUploadProgress(percentCompleted)
        }
      )

      const extractedData = response.data
      onSuccess?.(extractedData)
      return extractedData
    } catch (err) {
      const errorMessage = 'Error al subir el archivo. Por favor, intenta de nuevo.'
      setError(errorMessage)
      onError?.(errorMessage)
      return null
    } finally {
      setIsUploading(false)
      setUploadProgress(0)
    }
  }, [validateFile, currentTool, setUploadProgress, onSuccess, onError])

  const reset = useCallback(() => {
    setIsUploading(false)
    setProgress(0)
    setError(null)
  }, [])

  return {
    uploadFile,
    isUploading,
    progress,
    error,
    reset,
  }
}
