/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,jsx,ts,tsx}",
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  presets: [require("nativewind/preset")],
  theme: {
    extend: {
      colors: {
        // Surface tokens — backgrounds, cards, borders
        dark: {
          bg:          "#0B0F17",
          card:        "#131B2A",
          cardHover:   "#182338",
          border:      "#1F2E47",
          borderLight: "#2E4366",
        },
        // Semantic token palette — mirrors THEME_COLORS for className usage
        token: {
          primary:      "#3B82F6",
          primaryHover: "#2563EB",
          primaryIcon:  "#60A5FA",
          accent:       "#8B5CF6",
          accentIcon:   "#A78BFA",
          success:      "#10B981",
          successIcon:  "#34D399",
          warning:      "#F59E0B",
          warningIcon:  "#FBBF24",
          danger:       "#EF4444",
          dangerIcon:   "#F87171",
          muted:        "#94A3B8",
          dim:          "#64748B",
          disabled:     "#475569",
          company:      "#C084FC",
          owner:        "#818CF8",
          im:           "#38BDF8",
          relation:     "#F472B6",
          public:       "#2DD4BF",
        },
      },
    },
  },
  plugins: [],
};

