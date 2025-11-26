/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        midnight: "#0f172a",
        accent: "#f97316",
        teal: "#2dd4bf",
      },
    },
  },
  plugins: [],
};
