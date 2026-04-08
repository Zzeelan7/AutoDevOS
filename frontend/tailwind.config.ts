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
        // Core surfaces — warm off-whites and soft neutrals (Claude-like)
        surface: {
          DEFAULT: '#f9f7f4',
          subtle:  '#f2efe9',
          muted:   '#e8e3db',
          overlay: '#ffffff',
        },
        // Dark mode surfaces — warm charcoals, not pure black
        dark: {
          base:    '#1c1b18',
          raised:  '#242320',
          overlay: '#2c2b27',
          border:  '#38362f',
          hover:   '#302e29',
        },
        // Text hierarchy
        ink: {
          DEFAULT: '#1c1b18',
          secondary: '#57534a',
          muted:     '#a09b91',
          ghost:     '#ccc8c0',
        },
        // Accent — warm amber/terracotta, like Claude's highlights
        accent: {
          DEFAULT:  '#d97757',
          soft:     '#f5e6df',
          muted:    '#e8c4b3',
          strong:   '#b85c3d',
        },
        // Semantic colors — muted, warm-tinted
        success: { DEFAULT: '#4a7c59', soft: '#e6f0e9' },
        warning: { DEFAULT: '#a07840', soft: '#f5eddc' },
        danger:  { DEFAULT: '#9c3f38', soft: '#f5e0de' },
        info:    { DEFAULT: '#3d6b8c', soft: '#dceaf5' },
      },

      fontFamily: {
        sans:  ['Styrene B', 'Tiempos Text', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        serif: ['Tiempos Headline', 'Georgia', 'ui-serif', 'serif'],
        mono:  ['Berkeley Mono', 'Fira Code', 'ui-monospace', 'monospace'],
      },

      fontSize: {
        '2xs': ['0.6875rem', { lineHeight: '1rem' }],
        xs:    ['0.75rem',   { lineHeight: '1.125rem' }],
        sm:    ['0.875rem',  { lineHeight: '1.375rem' }],
        base:  ['0.9375rem', { lineHeight: '1.6rem' }],
        md:    ['1rem',      { lineHeight: '1.625rem' }],
        lg:    ['1.125rem',  { lineHeight: '1.75rem' }],
        xl:    ['1.25rem',   { lineHeight: '1.875rem' }],
        '2xl': ['1.5rem',    { lineHeight: '2rem',   letterSpacing: '-0.01em' }],
        '3xl': ['1.875rem',  { lineHeight: '2.375rem', letterSpacing: '-0.02em' }],
        '4xl': ['2.25rem',   { lineHeight: '2.75rem',  letterSpacing: '-0.025em' }],
        '5xl': ['3rem',      { lineHeight: '1.1',      letterSpacing: '-0.03em' }],
      },

      spacing: {
        '4.5': '1.125rem',
        '13':  '3.25rem',
        '18':  '4.5rem',
        '22':  '5.5rem',
        '26':  '6.5rem',
        '112': '28rem',
        '128': '32rem',
        '144': '36rem',
      },

      borderRadius: {
        'xs':  '0.25rem',
        'sm':  '0.375rem',
        DEFAULT: '0.5rem',
        'md':  '0.625rem',
        'lg':  '0.75rem',
        'xl':  '1rem',
        '2xl': '1.25rem',
        '3xl': '1.5rem',
      },

      boxShadow: {
        'xs':    '0 1px 2px 0 rgba(28,27,24,0.04)',
        'sm':    '0 1px 3px 0 rgba(28,27,24,0.06), 0 1px 2px -1px rgba(28,27,24,0.04)',
        DEFAULT: '0 2px 8px -1px rgba(28,27,24,0.08), 0 1px 3px -1px rgba(28,27,24,0.06)',
        'md':    '0 4px 16px -2px rgba(28,27,24,0.10), 0 2px 6px -2px rgba(28,27,24,0.06)',
        'lg':    '0 8px 32px -4px rgba(28,27,24,0.12), 0 4px 12px -4px rgba(28,27,24,0.06)',
        'xl':    '0 16px 48px -8px rgba(28,27,24,0.16), 0 8px 20px -8px rgba(28,27,24,0.08)',
        'inner-sm': 'inset 0 1px 2px 0 rgba(28,27,24,0.05)',
        'inner':    'inset 0 2px 4px 0 rgba(28,27,24,0.06)',
        // Dark mode shadows (use in .dark)
        'dark-sm': '0 1px 3px 0 rgba(0,0,0,0.3), 0 1px 2px -1px rgba(0,0,0,0.2)',
        'dark-md': '0 4px 16px -2px rgba(0,0,0,0.4), 0 2px 6px -2px rgba(0,0,0,0.3)',
        'dark-lg': '0 8px 32px -4px rgba(0,0,0,0.5), 0 4px 12px -4px rgba(0,0,0,0.3)',
        'none':  'none',
      },

      backgroundImage: {
        // Subtle paper texture for surfaces
        'surface-texture': "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='300'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='300' height='300' filter='url(%23noise)' opacity='0.03'/%3E%3C/svg%3E\")",
        // Warm gradient for hero areas
        'warm-gradient': 'linear-gradient(135deg, #f9f7f4 0%, #f0ece4 50%, #e8e0d4 100%)',
        'warm-gradient-dark': 'linear-gradient(135deg, #1c1b18 0%, #242320 50%, #1a1916 100%)',
        // Accent glow
        'accent-glow': 'radial-gradient(ellipse at top, rgba(217,119,87,0.08) 0%, transparent 70%)',
      },

      transitionTimingFunction: {
        'spring':     'cubic-bezier(0.34, 1.56, 0.64, 1)',
        'smooth':     'cubic-bezier(0.4, 0, 0.2, 1)',
        'in-smooth':  'cubic-bezier(0.4, 0, 1, 1)',
        'out-smooth': 'cubic-bezier(0, 0, 0.2, 1)',
        'snappy':     'cubic-bezier(0.25, 0.46, 0.45, 0.94)',
      },

      transitionDuration: {
        '50':  '50ms',
        '150': '150ms',
        '250': '250ms',
        '350': '350ms',
        '400': '400ms',
        '600': '600ms',
        '800': '800ms',
      },

      animation: {
        'fade-in':       'fadeIn 0.25s ease-out both',
        'fade-up':       'fadeUp 0.3s ease-out both',
        'fade-down':     'fadeDown 0.3s ease-out both',
        'scale-in':      'scaleIn 0.2s cubic-bezier(0.34,1.56,0.64,1) both',
        'slide-in-left': 'slideInLeft 0.3s ease-out both',
        'slide-in-right':'slideInRight 0.3s ease-out both',
        'pulse-soft':    'pulseSoft 2.5s ease-in-out infinite',
        'shimmer':       'shimmer 1.8s linear infinite',
        'typing':        'typing 1.2s steps(3,end) infinite',
      },

      keyframes: {
        fadeIn: {
          from: { opacity: '0' },
          to:   { opacity: '1' },
        },
        fadeUp: {
          from: { opacity: '0', transform: 'translateY(8px)' },
          to:   { opacity: '1', transform: 'translateY(0)' },
        },
        fadeDown: {
          from: { opacity: '0', transform: 'translateY(-8px)' },
          to:   { opacity: '1', transform: 'translateY(0)' },
        },
        scaleIn: {
          from: { opacity: '0', transform: 'scale(0.95)' },
          to:   { opacity: '1', transform: 'scale(1)' },
        },
        slideInLeft: {
          from: { opacity: '0', transform: 'translateX(-12px)' },
          to:   { opacity: '1', transform: 'translateX(0)' },
        },
        slideInRight: {
          from: { opacity: '0', transform: 'translateX(12px)' },
          to:   { opacity: '1', transform: 'translateX(0)' },
        },
        pulseSoft: {
          '0%, 100%': { opacity: '1' },
          '50%':      { opacity: '0.6' },
        },
        shimmer: {
          from: { backgroundPosition: '-200% center' },
          to:   { backgroundPosition: '200% center' },
        },
        typing: {
          '0%, 100%': { content: '▋' },
          '50%':      { opacity: '0' },
        },
      },

      maxWidth: {
        'prose-xs': '44ch',
        'prose-sm': '55ch',
        'prose':    '68ch',
        'prose-lg': '78ch',
        'chat':     '48rem',
        'page-sm':  '640px',
        'page':     '768px',
        'page-lg':  '1024px',
        'page-xl':  '1280px',
      },

      screens: {
        'xs': '480px',
      },

      zIndex: {
        '60':  '60',
        '70':  '70',
        '80':  '80',
        '90':  '90',
        '100': '100',
      },
    },
  },
  plugins: [],
}
export default config