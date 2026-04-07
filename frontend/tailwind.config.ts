import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        'brand-dark': '#0d0d0d',
        'brand-darker': '#050505',
        'brand-card': '#1a1a1a',
        'brand-border': '#2d2d2d',
        'brand-hover': '#262626',
      },
      backgroundColor: {
        'gradient-start': '#0d0d0d',
        'gradient-end': '#1a1a1a',
      },
    },
  },
  plugins: [],
}
export default config
