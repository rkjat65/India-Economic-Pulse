/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        bg:      '#0A0A0F',
        card:    '#12121C',
        sidebar: '#0D0D16',
        cyan:    { DEFAULT: '#06B6D4', 400: '#22D3EE', 500: '#06B6D4' },
        green:   { DEFAULT: '#22C55E', pulse: '#00D26A' },
        red:     { DEFAULT: '#EF4444' },
        amber:   { DEFAULT: '#F59E0B' },
        purple:  { DEFAULT: '#8B5CF6' },
        muted:   '#64748B',
        dim:     '#334155',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      borderColor: {
        DEFAULT: 'rgba(255,255,255,0.07)',
      },
    },
  },
  plugins: [],
}
