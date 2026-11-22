/**
 * Tailwind CSS configuration for MathGPT frontend.
 * Enables dark mode via class strategy and includes a custom gradient.
 */
module.exports = {
  darkMode: 'class', // use 'class' to toggle dark mode manually
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: '#0ea5e9', // teal-500
        surface: '#111827', // gray-900
        background: '#1f2937', // gray-800
      },
      backgroundImage: {
        'gradient-dark': 'radial-gradient(at top left, #1f2937, #111827)',
      },
    },
  },
  plugins: [],
};
