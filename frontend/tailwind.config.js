/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Colores principales GPT Legal
        gold: {
          DEFAULT: '#c4a35a',
          light: '#d4b86a',
          dark: '#b8963f',
          50: '#faf8f0',
        },
        cream: {
          DEFAULT: '#f5f0e6',
          light: '#faf8f5',
          dark: '#e8e0d0',
        },
        sage: {
          DEFAULT: '#f5f7f0',
          light: '#f8faf5',
        },
        // Semáforo de viabilidad
        viable: '#22c55e',
        inviable: '#eab308',
      },
      fontFamily: {
        heading: ['Space Grotesk', 'system-ui', 'sans-serif'],
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      backgroundImage: {
        'gradient-main': 'linear-gradient(135deg, #f5f7f0 0%, #faf8f5 100%)',
      },
      boxShadow: {
        'card': '0 2px 8px rgba(0, 0, 0, 0.06)',
        'card-hover': '0 4px 16px rgba(0, 0, 0, 0.1)',
      },
    },
  },
  plugins: [],
}
