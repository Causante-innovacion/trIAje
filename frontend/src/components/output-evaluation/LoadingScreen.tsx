import { Loader2 } from 'lucide-react'

export function LoadingScreen() {
    return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center">
            <div className="text-center">
                <div className="mb-6 flex justify-center">
                    <div className="bg-yellow-400 w-16 h-16 transform rotate-45 rounded-lg flex items-center justify-center">
                        <Loader2 className="w-8 h-8 text-white animate-spin -rotate-45" />
                    </div>
                </div>
                <h2 className="text-2xl font-bold text-gray-900 mb-2">
                    Analizando tu proyecto
                </h2>
                <p className="text-gray-600 max-w-md">
                    Estamos procesando la información legal de tu organización y generando recomendaciones personalizadas...
                </p>
            </div>
        </div>
    )
}
