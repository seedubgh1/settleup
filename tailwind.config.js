/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./static/**/*.js",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['DM Sans', 'sans-serif'],
        display: ['Playfair Display', 'serif'],
        mono: ['DM Mono', 'monospace'],
      },
      colors: {
        surface: {
          DEFAULT: '#0f1117',
          raised: '#161b27',
          border: '#1e2535',
        },
        accent: {
          DEFAULT: '#4ade80',
          muted: '#166534',
          dim: '#14532d',
        },
        ink: {
          DEFAULT: '#f1f5f9',
          muted: '#94a3b8',
          dim: '#475569',
        },
      },
    },
  },
  plugins: [],
}
