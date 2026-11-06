/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        coal: {
          950: "#0b0607",
          900: "#160e10",
          800: "#2a181b",
          700: "#3d2428",
          600: "#57343a",
        },
      },
    },
  },
  plugins: [],
};
