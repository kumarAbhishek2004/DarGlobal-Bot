/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        gold: {
          light: '#F4E5B8',
          DEFAULT: '#D4AF37',
          dark: '#8C6D23',
        },
        obsidian: {
          DEFAULT: '#0B0F17',
          card: '#131926',
          border: '#1F293D',
        }
      }
    },
  },
  plugins: [],
}
