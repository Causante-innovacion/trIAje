import { useState, useEffect } from 'react'

const LOADING_STEPS = [
    'Analizando estructura legal...',
    'Evaluando organizaciones...',
    'Revisando normativa aplicable...',
    'Generando recomendaciones...',
]

export function LoadingScreen() {
    const [stepIndex, setStepIndex] = useState(0)

    useEffect(() => {
        const interval = setInterval(() => {
            setStepIndex(prev => (prev + 1) % LOADING_STEPS.length)
        }, 1800)
        return () => clearInterval(interval)
    }, [])

    return (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50">
            <div className="bg-white rounded-2xl p-10 text-center shadow-2xl animate-slide-up max-w-sm mx-4">
                <div className="w-14 h-14 border-4 border-gold border-t-transparent rounded-full animate-spin mx-auto mb-6" />
                <h2 className="text-xl font-bold text-gray-900 mb-2">
                    Analizando tu proyecto
                </h2>
                <p className="text-sm text-gray-500 h-5 transition-all duration-300">
                    {LOADING_STEPS[stepIndex]}
                </p>
                <div className="mt-6 flex justify-center gap-1.5">
                    {LOADING_STEPS.map((_, i) => (
                        <div
                            key={i}
                            className={`w-2 h-2 rounded-full transition-all duration-300 ${
                                i === stepIndex ? 'bg-gold w-6' : 'bg-gray-200'
                            }`}
                        />
                    ))}
                </div>
            </div>
        </div>
    )
}
