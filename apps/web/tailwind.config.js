/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        primary: "#64748B",
        accent: "#EA580C",
        ink: "#334155",
        canvas: "#F8FAFC",
        muted: "#EBF0F5",
      },
      fontFamily: {
        sans: ["Fira Sans", "Segoe UI", "sans-serif"],
        mono: ["Fira Code", "ui-monospace", "monospace"],
      },
    },
  },
  plugins: [],
};
