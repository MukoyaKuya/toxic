/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './web/templates/**/*.html',
    './**/forms.py',
    './**/views.py'
  ],
  theme: {
    extend: {
      colors: {
        toxicBlack: '#0a0a0a',
        toxicGray: '#151515',
        toxicAccent: '#e11d48', // Rose-600
        cream: '#f5f0e6',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        display: ['Oswald', 'sans-serif'],
        grandover: ['Grandover', 'sans-serif'],
      },
      keyframes: {
        'fade-in-up': {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        }
      },
      animation: {
        'fade-in-up': 'fade-in-up 1s ease-out forwards',
      }
    }
  },
  plugins: [],
}
