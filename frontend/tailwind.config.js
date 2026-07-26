/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#eef7ff",
          100: "#d9edff",
          500: "#2f7fe0",
          600: "#2364b8",
          700: "#1c4f93",
        },
      },
    },
  },
  plugins: [],
}
