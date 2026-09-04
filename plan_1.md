# UI POLISH SPECIFICATION: VISUAL REFINEMENT & LEGIBILITY
### Target: Solid Card Opacity, Type Scaling, and Contrast Hardening

---

## 1. Eliminate Transparency on All Cards
In `MetricCard.jsx`, `RemediationDeck.jsx`, `CategoryVisualizer.jsx`, and `StructuralImpactCard.jsx`:
- Remove tinted translucent fills (`bg-destructive/5`, `bg-secondary/30`, `bg-primary/5`).
- Enforce solid, opaque card backgrounds: `bg-card` (which maps to solid white in light mode, solid `#121215` in dark mode).
- In `MetricCard.jsx`, rely strictly on a solid top-border or left-border accent (2px) and distinct text color for status differentiation.

## 2. Background Dot Pattern Subtlety
In `App.jsx`, lower the background dot grid opacity from `opacity-40` to `opacity-15 dark:opacity-20` so it acts as subtle atmospheric texture rather than clashing with foreground text.

## 3. Typography & Hierarchy Scale-Up
- **KPI Metrics (`MetricCard.jsx`):** Bump titles from `text-[11px]` to `text-xs font-bold tracking-wider text-muted-foreground uppercase`. Bump subtitles from `text-xs` to `text-sm font-medium text-foreground/80`.
- **Explanations & Body Text:** In `RemediationDeck.jsx` and `AuditTrailTable.jsx`, upgrade body descriptions from `text-xs` to `text-sm leading-relaxed text-foreground/90`.
- **Table Ledger (`AuditTrailTable.jsx`):** Bump table headers to `text-xs font-semibold text-foreground/70`, and cell text to `text-sm` for numbers and deltas.

## 4. Light/Dark Mode Contrast Tuning (`index.css`)
Adjust CSS variables for higher legibility:
- In `:root` (light mode), set `--muted-foreground: #52525b;` (darker gray for daylight reading) and `--card: #ffffff;`.
- In `.dark`, set `--muted-foreground: #a1a1aa;` and ensure `--card: #111114;` is completely opaque.

---
Verify with `npm run build`. Output: `PASS: Visual polish applied.`