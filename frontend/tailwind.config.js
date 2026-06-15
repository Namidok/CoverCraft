/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        accent: "#10B981",
        "accent-hover": "#059669",
        surface: "#FAFAFA",
        card: "#FFFFFF",
        border: "#E5E7EB",
        muted: "#9CA3AF",
        subtle: "#6B7280",
        dark: "#1a1a1a",
      },
    },
  },
  plugins: [],
}