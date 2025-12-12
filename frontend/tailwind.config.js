/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#2563eb',
        secondary: '#10b981',
        accent: '#f59e0b',
        background: '#f1f5f9',       // ✅ top-level key
        card: '#ffffff',
        'text-primary': '#1e293b',   // flatten nested keys
        'text-secondary': '#475569',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        soft: '0 4px 6px -1px rgba(0,0,0,0.05), 0 2px 4px -1px rgba(0,0,0,0.03)',
        medium: '0 10px 15px -3 rgba(0,0,0,0.08), 0 4px 6px -2 rgba(0,0,0,0.05)',
      },
    },
  },
  plugins: [],
}
