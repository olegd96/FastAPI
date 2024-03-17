/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["../templates/*.html"],
  theme: {
    extend: {},
  },
  plugins: [require("daisyui")],
  corePlugins: {
    preflight: false,
  },
  prefix: 'tw-',
}

