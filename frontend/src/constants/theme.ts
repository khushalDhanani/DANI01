/**
 * AIRIS Insights — Centralized Design Token System
 *
 * Single source of truth for all colors used in the application.
 * Every icon `color={}` prop and inline style MUST reference a token from here.
 * No bare hex strings (#xxxxxx) should appear in any component file.
 *
 * Organized by:
 *   1. Surface tokens  — backgrounds, cards, borders
 *   2. Text tokens     — readable text on dark surfaces
 *   3. Semantic fills  — status bg/fill colors (used in Tailwind classes)
 *   4. Semantic icons  — lighter shades for icon color= props on dark bg
 *   5. Domain icons    — entity-specific icon colors
 */
export const THEME_COLORS = {
  // ── 1. Surface Tokens ─────────────────────────────────────────
  bg:           "#0B0F17",  // page background
  card:         "#131B2A",  // card / panel background
  cardHover:    "#182338",  // card hover state
  border:       "#1F2E47",  // default border
  borderLight:  "#2E4366",  // lighter border / divider
  skeleton:     "#334155",  // placeholder skeleton background

  // ── 2. Text Tokens ────────────────────────────────────────────
  textPrimary:  "#FFFFFF",  // primary heading / value text
  textMuted:    "#94A3B8",  // secondary / helper text (slate-400)
  textDark:     "#64748B",  // disabled / dimmed text (slate-500)
  textDisabled: "#475569",  // very dimmed / placeholder (slate-600)

  // ── 3. Semantic Fill Colors (for bg/border Tailwind classes) ──
  primary:      "#3B82F6",  // blue-500   — primary action
  primaryHover: "#2563EB",  // blue-600   — primary hover
  accent:       "#8B5CF6",  // violet-500 — accent
  success:      "#10B981",  // emerald-500 — success fill
  warning:      "#F59E0B",  // amber-500  — warning fill
  danger:       "#EF4444",  // red-500    — danger fill

  // ── 4. Semantic Icon Colors (lighter shades; readable on dark bg) ──
  primaryIcon:  "#60A5FA",  // blue-400   — primary icon, links, active tab
  successIcon:  "#34D399",  // emerald-400 — success icon, phone, active
  warningIcon:  "#FBBF24",  // amber-400  — warning icon, keys, indexes, date
  dangerIcon:   "#F87171",  // red-400    — error/danger icon, lock
  accentIcon:   "#A78BFA",  // violet-400 — accent icon, contacts tab
  onPrimary:    "#FFFFFF",  // white      — icon/text rendered on a colored bg

  // ── 5. Domain / Entity Icon Colors ───────────────────────────
  companyIcon:  "#C084FC",  // purple-400 — company / organization links
  ownerIcon:    "#818CF8",  // indigo-400 — owner / PR fields
  imIcon:       "#38BDF8",  // sky-400    — IM / messaging handles
  relationIcon: "#F472B6",  // pink-400   — personal relationship links
  publicIcon:   "#2DD4BF",  // teal-400   — public / share-contact indicator
};

