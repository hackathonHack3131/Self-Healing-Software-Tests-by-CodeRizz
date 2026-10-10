import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",
        surface: {
          50: "#161E2E",
          100: "#131A29",
          200: "#0F1622",
          300: "#0B1019",
          400: "#080C13",
        },
        navy: {
          900: "#070A11",
          850: "#0B0F19",
          800: "#0E1524",
          700: "#152035",
          600: "#1E2D4A",
        },
        brand: {
          violet: {
            DEFAULT: "#8B5CF6",
            light: "#A78BFA",
            dark: "#6D28D9",
            glow: "rgba(139, 92, 246, 0.35)",
          },
          cyan: {
            DEFAULT: "#06B6D4",
            light: "#22D3EE",
            dark: "#0891B2",
            glow: "rgba(6, 182, 212, 0.35)",
          },
          emerald: {
            DEFAULT: "#10B981",
            light: "#34D399",
            dark: "#059669",
          },
          rose: {
            DEFAULT: "#F43F5E",
            light: "#FB7185",
            dark: "#E11D48",
          },
          amber: {
            DEFAULT: "#F59E0B",
            light: "#FBBF24",
            dark: "#D97706",
          }
        }
      },
      fontFamily: {
        sans: ["var(--font-inter)", "system-ui", "sans-serif"],
        mono: ["var(--font-mono)", "monospace"],
      },
      boxShadow: {
        "glow-violet": "0 0 25px -5px rgba(139, 92, 246, 0.4)",
        "glow-cyan": "0 0 25px -5px rgba(6, 182, 212, 0.4)",
        "glow-emerald": "0 0 25px -5px rgba(16, 185, 129, 0.4)",
        "glass": "0 8px 32px 0 rgba(0, 0, 0, 0.37)",
      },
      animation: {
        "pulse-slow": "pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "shimmer": "shimmer 2.5s linear infinite",
      },
      keyframes: {
        shimmer: {
          "0%": { backgroundPosition: "-200% 0" },
          "100%": { backgroundPosition: "200% 0" },
        }
      }
    },
  },
  plugins: [],
};
export default config;
