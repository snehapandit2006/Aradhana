/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        cosmic: {
          dark: '#0a0e1a',      // Midnight Navy
          gold: '#c9a84c',      // Soft Gold
          lavender: '#9b8ec4',  // Muted Lavender
          silver: '#e2e8f0',    // Cosmic Dust Silver
          slate: '#1a1f35',     // Lighter cosmic background
        }
      },
      fontFamily: {
        serif: ['"Playfair Display"', 'Georgia', 'serif'],
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        'gold-glow': '0 0 15px rgba(201, 168, 76, 0.15)',
        'lavender-glow': '0 0 15px rgba(155, 142, 196, 0.15)',
        'nebula': '0 0 40px rgba(155, 142, 196, 0.05)',
      },
      backgroundImage: {
        'cosmic-gradient': 'radial-gradient(circle at 50% 50%, #1a1f35 0%, #0a0e1a 100%)',
        'gold-gradient': 'linear-gradient(to right, #c9a84c, #e5c158)',
      }
    },
  },
  plugins: [],
}
