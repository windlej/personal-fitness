# Design system — "Y2K × Nature"

**Living document.** This is the source of truth for how the app looks, feels,
and moves. When you change the design, change this file too. The implemented
tokens live in `css/styles.css` (`:root` + dark-mode block); everything below
should mirror them. Icons and inline SVG live in `js/app.js` (the `ICONS` map +
`icon()` helper) and `index.html` (tabs / topbar).

> Changing the plan content is a different job — see
> `.opencode/skills/modify-training-plan/SKILL.md`. This doc is about the visual
> language only.

---

## 1. Core feeling

Clean, modern web app. **Not** a sporty fitness app, **not** a SaaS dashboard.
Think the aerodynamic racing lines of a Formula-1 car crossed with the quiet
calm of a singletrack trail. Elegant motion, natural flow, refined energy.

**Aesthetic direction: Y2K × Nature.** Early-2000s digital optimism (soft gloss,
rounded forms, subtle metallic warmth, playful but refined) grown over organic
terrain. Nature feels slightly futuristic; the tech feels grounded and alive.
Neither pure cyber-chrome Y2K nor earthy-minimal — the hybrid is the point.

---

## 2. Palette (strict)

Seven colors. No foreign hues — build tints, shades, and washes by mixing these
together or with `color-mix(... , #FFFDF8)` / `... , transparent`. Raw hex is
allowed only for the palette itself and the two near-neutral anchors
(`#FFFDF8`, `#2E3324`) and their dark-mode counterparts.

| Token | Hex | Name | Role |
|-------|-----|------|------|
| `--olive` | `#797D62` | Dusty Olive | Structure, deep ground, long-run green |
| `--palm` | `#9B9B7A` | Palm Leaf | Easy / Z2 growth |
| `--sand` | `#D9AE94` | Desert Sand | Warmth, speed accent |
| `--peach` | `#F1DCA7` | Soft Peach | Soft glow, ambient light |
| `--pollen` | `#FFCB69` | Golden Pollen | **Energy accent** (glow, highlights, VO2) |
| `--almond` | `#D08C60` | Toasted Almond | **Primary interactive** (buttons, links, threshold) |
| `--taupe` | `#997B66` | Dusty Taupe | Depth, earth, race/TT |

Contrast rule of thumb: olive/taupe for structure and depth; **Golden Pollen and
Soft Peach are energy — use them sparingly**, as glow, gradients, and single
accents. When in doubt, less accent.

---

## 3. Semantic tokens

These are the names components should use (not raw palette names). Defined in
`css/styles.css :root`, overridden in the `prefers-color-scheme: dark` block.

### Surfaces & ink

| Token | Light | Dark | Use |
|-------|-------|------|-----|
| `--bg` | `#FBF4E5` | `#20241A` | Page ground (warm cream / deep olive) |
| `--surface` | `#FFFDF8` | `#2A2F22` | Cards, modals |
| `--surface-2` | sand 15% | `#343A2A` | Fills, inputs, hover rows |
| `--surface-3` | olive 9% | `#3B4130` | Recessed blocks (KB) |
| `--border` / `--border-soft` | olive 26% / 14% | `#4B5240` / `#3D4433` | Structural / hairline lines |
| `--text` | `#2E3324` | `#F2ECD8` | Primary ink |
| `--muted` | `#6E7260` | `#B7B79F` | Secondary text |
| `--faint` | `#9B9C88` | `#8B8B74` | Tertiary / footer |

### Accent

| Token | Light | Dark | Use |
|-------|-------|------|-----|
| `--accent` | `--almond` | `#E0A578` | Primary interactive fills/graphics |
| `--accent-ink` | almond 62% + brown | `#F2C39B` | Readable accent **text** |
| `--accent-soft` | almond 17% wash | almond 24% | Tints, focus rings |
| `--energy` | `--pollen` | `#FFD57F` | Glow / highlight |
| `--energy-soft` | pollen 34% wash | pollen 20% | Energy backgrounds |
| `--glow-1..3` | peach / pollen / sand | low-alpha pollen / almond / sand | Ambient body gradient |

### Session kinds (drive chips, calendar sparks, bars, legends)

| Kind | Token pair | Maps from | Color family |
|------|-----------|-----------|--------------|
| Easy / Z2 | `--z2` / `--z2-bg` | `kind: easy`, `zone: Z2`, template `easy` | Palm / olive green |
| Threshold / Z4 | `--z4` / `--z4-bg` | `kind: threshold`, `zone: Z4` | Toasted Almond |
| VO2 / Z5 | `--z5` / `--z5-bg` | `kind: vo2`, `zone: Z5` | Golden Pollen |
| Speed / strides | `--spd` / `--spd-bg` | `kind: speed`, `zone: SPD` | Desert Sand |
| Race / TT | `--test` / `--test-bg` | `kind: test`, `zone: TEST` | Dusty Taupe |
| Long run | `--long` / `--long-bg` | `kind: long` | Dusty Olive |
| Rest | `--rest` / `--rest-bg` | `kind: rest` | Muted olive-grey |

`js/app.js` maps a day to one of these classes via `chipClass()` and
`colorVar()` — **keep those class names and the paired `-bg` tokens in sync**.

---

## 4. Typography

- **Body / UI:** `Work Sans` (weights 300–700), `--font`. Base **15px / 1.55**.
- **Display:** `Montserrat` (500–800), `--font-display`. Used for the hero
  session title, brand wordmark, big stat numbers, calendar month, section
  display headings, plan title. Large headlines only — never body copy.
- Loaded from Google Fonts via `<link>` in `index.html` (static, no build).

Scale in use: hero h1 `26px → 22px` on mobile; stat value `28px`; card title
`12.5px` uppercase `0.1em` tracking; body `15px`; small `12.5px`; labels `12px`
uppercase. Headings use tight tracking (`-.01em` / `-.02em`). Never set body
text below 12px.

---

## 5. Space, radius, elevation, motion

- **Spacing:** deliberate, breathing rhythm around a 4px base — card padding
  `22px` (`18px` mobile), main gap `18px`, section gap `14px`, control padding
  `11–13px`. Favor negative space over density.
- **Radius:** `--radius-lg: 28px` (hero/modal), `--radius: 20px` (cards),
  `--radius-sm: 14px` (controls), `--radius-xs: 10px` (calendar), `--pill: 999px`
  (chips, buttons, bars). Rounded forms are part of the Y2K feel.
- **Elevation:** light and warm, never heavy. `--shadow` (cards), `--shadow-sm`
  (hover lift), plus `--gloss` — an inset top highlight that reads as soft gloss
  rather than plastic. Colored chips/cards use `box-shadow: var(--gloss)`.
- **Motion:** `--ease: cubic-bezier(.22,.61,.36,1)`, `--dur: .28s`. Gliding, not
  springy. Cards `rise` in on render; hover states translate `-1px`; modals fade
  + rise. Always honor `prefers-reduced-motion` (already wired).
- **Interactive minimums:** tap targets ≥ 40–42px (`nav-btn` 42px, buttons
  ≥ 44px tall via padding); focus-visible ring uses `--accent`.

---

## 6. Icons — Lucide only

One system: **Lucide** (ISC), inline SVG, `stroke-width: 2`, round caps/joins,
`currentColor`. No emoji, no other icon sets, no-filled shapes.

- Static (tabs, topbar, brand): inline `<svg class="ico">` in `index.html`.
- Dynamic (nav chevrons, `+`, `✕`, clock, dumbbell, target, file/upload/trash):
  the `ICONS` map + `icon(name)` helper in `js/app.js`.
- Size via `.ico` (`18px`, context overrides to `13–16px`). Color inherits from
  the parent; the active tab tints its icon `--energy`.
- To add one: fetch the glyph from <https://lucide.dev/icons/> (or
  `lucide-static`), paste its inner markup into `ICONS`, and use `icon("name")`.

---

## 7. Components (patterns to reuse)

- **Topbar** — translucent warm glass (`backdrop-filter` blur), hairline border,
  brand mark = gradient pollen→almond rounded chip with the activity glyph.
- **Tabs** — horizontally scrolling pill row; active = solid ink pill with an
  energy-tinted icon. Sticky under the topbar (`--topbar-h`).
- **Card** — `--surface`, `--radius`, `--shadow + --gloss`; `pad-0` removes
  padding for list cards. `.card-title` carries the gradient tick (`::before`).
- **Hero (Today)** — `--radius-lg`, gradient `--c` stripe, faint twin
  racing-line SVG sweep (`raceLines()`), chips, then the pace-target pill.
- **Chips** — pill, `.dot` for intensity, Lucide glyph for duration; semantic
  kind classes (`.z2/.z4/.z5/.spd/.test/.long/.rest/.ghost`).
- **Detail list** — recessed rows with a pollen→almond bullet.
- **KB block** — dashed recess with dumbbell glyph + `KB A/B/C` badge.
- **Bars / charts** — pill tracks; `.bar-fill.actual` is an energy→accent
  gradient. (Note: JS passes explicit `var(--kind)` fills for adherence bars.)
- **Stat** — airy, not boxed: left rule + Montserrat number + label.
- **Modal / toast** — `--radius-lg`, blurred backdrop, `rise`/`pop` motion.
- **Racing-line details** — gradient tick before every `card-title`; the hero
  sweep; a nose-like gradient on primary buttons.

---

## 8. Layout

- Max width `--maxw: 920px`, centered, generous gutters (`18px`).
- **Stacked, breathing sections** — not a dense grid of KPI cards. Open,
  intentional negative space.
- Single-column on mobile; `grid-2` / `grid-3` collapse to one column ≤ 520px.
- Safe areas respected (topbar `padding-top`, body/footer `env(safe-area-inset)`).
- No horizontal scroll except intentional `.scroll-x` for wide tables/tabs.

---

## 9. Anti-patterns — do not do

- Hyper-sporty / high-adrenaline looks: neon, black/red, aggressive angles,
  "beast mode" language.
- Generic SaaS dashboard: dense card grids, heavy sidebars, metric walls,
  generic data tables as the primary surface.
- Flat Material elevation or brutalist edges.
- Over-glossy plastic Y2K that reads dated rather than refined.
- Cool did not appear: no blues/purples/greys from outside the palette (verify a
  rendered screenshot has ~0% cool pixels).
- Emoji as icons; mixed icon sets; mixed corner radii; one duration for every
  transition; animating width/height.
- Cramped density, hard rectangular boxes, text under 12px, gray-on-gray.

---

## 10. Files & how to change it

| File | Owns |
|------|------|
| `css/styles.css` | All tokens, components, motion, dark mode. **Start here.** |
| `index.html` | Font links, theme-color, favicon, static tab/topbar Lucide icons |
| `js/app.js` | `ICONS` + `icon()` helper, `raceLines()`, semantic kind classes |

**Workflow for a visual change:** edit the token in `css/styles.css`, then any
component using it updates automatically; update this doc's tables if a token
value changes. Re-check both light and dark. Quick visual QA (no build needed):

```bash
# renders each view; headless Chrome, no install
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
"$CHROME" --headless=new --hide-scrollbars --window-size=1000,1500 \
  --virtual-time-budget=5000 --screenshot=/tmp/day.png \
  "file://$PWD/index.html#day"
```

(Headless defaults to dark; add `--blink-settings=preferredColorScheme=1` for
light.)

---

## Changelog

- **2026-10-12** — Initial system. Replaced the blue/slate UI with the strict
  Y2K × Nature palette, Work Sans + Montserrat, Lucide icons, rounded/gloss
  tokens, racing-line accents, and a full light/dark pass.
