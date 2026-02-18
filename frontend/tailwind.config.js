/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // ── Causante Design System ──
        // Primary
        causante: {
          yellow: '#d7d100',
          purple: '#8f86a3',
          green: '#d0dbce',
          ocre: '#b3994c',
        },
        // Functional aliases
        gold: {
          DEFAULT: '#b3994c',
          light: '#c9b06a',
          dark: '#9a8340',
          50: '#faf8f0',
        },
        cream: {
          DEFAULT: '#f7f5f0',
          light: '#faf9f6',
          dark: '#ede9e0',
        },
        // Semáforo de chat inteligente
        semaphore: {
          green: '#059669',
          yellow: '#d97706',
          red: '#dc2626',
        },
        // Legacy
        viable: '#22c55e',
        inviable: '#eab308',
      },
      fontFamily: {
        heading: ['Space Grotesk', 'system-ui', 'sans-serif'],
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      borderRadius: {
        '4xl': '2rem',
      },
      boxShadow: {
        'card': '0 1px 3px rgba(0, 0, 0, 0.04), 0 1px 2px rgba(0, 0, 0, 0.03)',
        'card-hover': '0 4px 12px rgba(0, 0, 0, 0.06)',
        'input': '0 1px 2px rgba(0, 0, 0, 0.04)',
      },
      animation: {
        'fade-in': 'fadeIn 0.3s ease-out',
        'slide-up': 'slideUp 0.4s ease-out forwards',
        'slide-in': 'slideIn 0.3s ease-out both',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0', transform: 'translateY(4px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(16px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideIn: {
          '0%': { opacity: '0', transform: 'translateX(-8px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
      },
    },
  },
  plugins: [],
}
