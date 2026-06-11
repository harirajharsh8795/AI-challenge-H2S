/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          dark: "#090D16",
          card: "#0E1524",
          border: "#1E293B",
          orange: "#FF6B00",
          purple: "#6366F1",
          teal: "#14B8A6",
          gray: "#94A3B8"
        }
      },
      fontFamily: {
        sans: ["Inter", "Outfit", "system-ui", "sans-serif"],
      },
      boxShadow: {
        glass: "0 8px 32px 0 rgba(0, 0, 0, 0.37)",
        "glass-orange": "0 8px 32px 0 rgba(255, 107, 0, 0.15)",
      }
    },
  },
  plugins: [],
}
