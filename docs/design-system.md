# Design system — "Orbital Contour Map" (chrome-tinged Y2K × Nature)

**Living document.** This is the source of truth for how the app looks, feels,
and moves. When you change the design, change this file too. The implemented
tokens live in `css/styles.css` (`:root` + dark-mode block); everything below
mirrors them. Icons and inline SVG live in `js/app.js` (the `ICONS` map,
`icon()`, `orbitLines()`, `terrainField()`) and `index.html` (tabs / topbar).

> Changing the plan content is a different job — see
> `.opencode/skills/modify-training-plan/SKILL.md`. This doc is about the visual
> language only.

---

## 1. Core feeling

**Orbital Contour Map.** Today is the **central focal node** — a soft, slightly
glossy, liquid-edged digital object resting in a topographic terrain. The days
and context around it ride **organic, slightly irregular orbits**, joined by
smooth racing-line curves. The ground is a **soft contour field**.

**Aesthetic: chrome-tinged Y2K × Nature.** Nature gives earthy terrain, contour
language, organic irregularity, mountain-trail quiet. Y2K gives soft gloss,
pearl and chrome accents, gentle specular highlights, higher contrast, and
subtle digital optimism. The centerpiece should feel like a polished digital
object set down in a natural landscape.

**Not** a typical fitness app, **not** a SaaS dashboard. No generic radial
charts, no perfect geometric orbits, no flat card stacks, no default
component-library UI.

---

## 2. Palette (strict)

Eight colors. No foreign hues — build tints, shades, and washes by mixing these
with each other or with near-neutral anchors (`#FFFFFF`, deep ink) and
`transparent`. Raw hex is allowed only for the palette itself, the anchors, and
their dark-mode counterparts.

| Token | Hex | Name | Role |
|-------|-----|------|------|
| `--deep` | `#3F4738` | Deep Structure | Ground, ink, rest, dark-mode base |
| `--terrain` | `#6F7A62` | Mid Terrain | Structure, long / easy growth |
| `--earth` | `#C9A07A` | Warm Earth | Warmth, speed / strides |
| `--light` | `#F5EDDF` | Light Surface | Paper, dark-mode ink |
| `--gold` | `#E6B84D` | Liquid Gold | **Primary energy** — active, glow, VO2 |
| `--copper` | `#C67B4A` | Burnt Copper | **Primary interactive** — buttons, threshold |
| `--chrome` | `#C8CDC7` | Chrome / Metallic | Rims, specular, neutral, rest |
| `--cool` | `#A8B5A0` | Cool Contrast | Calm green counterpoint, easy / Z2 |

Rule of thumb: terrain colors stay **dominant**; **Liquid Gold + Soft Chrome**
are for energy, active states, and highlights. When in doubt, less gold.

---

## 3. Semantic tokens

Components use these names (not raw palette names). Defined in
`css/styles.css :root`, overridden in the `prefers-color-scheme: dark` block.

### Surfaces & ink

| Token | Light | Dark | Use |
|-------|-------|------|-----|
| `--bg` | `--light` | `#2A3024` | Page ground (warm paper / deep olive) |
| `--surface` | light 42% + white | `#363D2D` | Cards, modals (pearl tint) |
| `--surface-2` | terrain 9% wash | `#414A37` | Fills, inputs, hover rows |
| `--surface-3` | terrain 15% wash | `#4A5340` | Recessed blocks (KB) |
| `--border` / `--border-soft` | deep 24% / 13% | `#5C6449` / `#464F3A` | Structural / hairline lines |
| `--text` | `--deep` | `--light` | Primary ink |
| `--muted` | deep 62% + terrain | `#B9C0AC` | Secondary text |
| `--faint` | terrain 72% + light | `#8A9280` | Tertiary / footer |

### Accent, chrome, terrain

| Token | Light | Dark | Use |
|-------|-------|------|-----|
| `--accent` | `--copper` | `#D89060` | Primary interactive fills/graphics |
| `--accent-ink` | copper 62% + `#3A1C0C` | `#EEB98C` | Readable accent **text** |
| `--accent-soft` | copper 15% wash | copper 22% | Tints, focus rings |
| `--energy` | `--gold` | `#F0C963` | Glow / highlight / active |
| `--energy-soft` | gold 30% wash | gold 20% | Energy backgrounds |
| `--chrome-soft` | chrome 62% + white | chrome 24% | Rims, specular neutral |
| `--node-hi/mid/lo` | white → gold → earth/copper | dark sheen | Central node gradient |
| `--glow-1..3` | earth / gold / terrain | low-alpha | Ambient body light |
| `--terrain-line` / `--terrain-gold` | terrain / gold, low alpha | lower alpha | Contour field strokes |

### Session kinds (drive chips, calendar sparks, bars, legends)

| Kind | Token pair | Maps from | Color family |
|------|-----------|-----------|--------------|
| Easy / Z2 | `--z2` / `--z2-bg` | `kind: easy`, `zone: Z2`, template `easy` | Cool contrast green |
| Threshold / Z4 | `--z4` / `--z4-bg` | `kind: threshold`, `zone: Z4` | Burnt Copper |
| VO2 / Z5 | `--z5` / `--z5-bg` | `kind: vo2`, `zone: Z5` | Liquid Gold |
| Speed / strides | `--spd` / `--spd-bg` | `kind: speed`, `zone: SPD` | Warm Earth |
| Race / TT | `--test` / `--test-bg` | `kind: test`, `zone: TEST` | Deep + Copper |
| Long run | `--long` / `--long-bg` | `kind: long` | Mid Terrain |
| Rest | `--rest` / `--rest-bg` | `kind: rest` | Terrain / chrome |

`js/app.js` maps a day to one of these via `chipClass()` and `colorVar()` —
**keep those class names and the paired `-bg` tokens in sync**. All kind
foregrounds are tuned to ≥ 4.5:1 against their own `-bg` in both themes.

---

## 4. Typography

- **Everything:** `Work Sans` (weights 300–800), `--font` / `--font-display`.
  Base **15px / 1.55**. No second family — display is simply Work Sans at
  weight 700–800 with tighter tracking (`-.015em` / `-.03em`). One coherent
  voice, less default-library feel.
- Loaded from Google Fonts via `<link>` in `index.html` (static, no build).

Scale in use: central node h1 `27px → 22px` on mobile; stat value `28px`; card
title `12.5px` uppercase `0.12em` tracking; node kicker `11.5px` uppercase
`0.16em`; body `15px`; small `12.5px`; labels `12px` uppercase. Never set body
text below 12px.

---

## 5. Space, radius, elevation, motion

- **Spacing:** deliberate, breathing rhythm around a 4px base — card padding
  `22px` (`18px` mobile), main gap `18px`, section gap `14px`, control padding
  `11–13px`. Favor negative space over density.
- **Radius:** `--radius-lg: 30px` (hero node/modal), `--radius: 22px` (cards),
  `--radius-sm: 15px` (controls), `--radius-xs: 11px`, `--pill: 999px`. Organic,
  **irregular** radii are the signature: the node, brand mark, nav buttons and
  calendar cells use asymmetric liquid-edges (e.g.
  `47% 53% 45% 55% / 55% 46% 54% 45%`), week rows use
  `16px 20px 16px 20px / 20px 16px 20px 16px`.
- **Elevation:** light and warm, never heavy. `--shadow` (cards), `--shadow-sm`
  (hover lift), `--gloss` / `--gloss-strong` — inset highlights that read as
  **soft gloss / specular** rather than plastic; `--rim` is the chrome hairline.
  The central node combines all three plus a **conic chrome↔gold bezel** (`::before`
  with `mask-composite: exclude`). Cards are **translucent warm glass**
  (`backdrop-filter: blur(14px)`) so the contour terrain reads through them — the
  "objects resting in a landscape" effect. The active tab and status pills are
  chrome→gold gradients with deep ink.
- **Motion:** `--ease: cubic-bezier(.22,.61,.36,1)`, `--dur: .28s`. Gliding, not
  springy. Cards `rise` in on render; hover translates `-1px`; modals fade +
  rise. Always honor `prefers-reduced-motion` (wired).
- **Interactive minimums:** tap targets ≥ 40–42px; focus-visible ring uses
  `--accent`.

---

## 6. Icons — Lucide only

One system: **Lucide** (ISC), inline SVG, **`stroke-width: 1.75`** (medium,
slightly rounded), round caps/joins, `currentColor`. No emoji, no other icon
sets, no filled shapes.

- Static (tabs, topbar, brand): inline `<svg class="ico">` in `index.html`.
- Dynamic (nav chevrons, `+`, `✕`, clock, dumbbell, target, file/upload/trash):
  the `ICONS` map + `icon(name)` helper in `js/app.js`.
- Size via `.ico` (`18px`, context overrides to `13–16px`). Color inherits; the
  active tab tints its icon `--energy`.
- To add one: fetch the glyph from <https://lucide.dev/icons/>, paste its inner
  markup into `ICONS`, and use `icon("name")`.

---

## 7. Components (patterns to reuse)

- **Contour terrain** — a fixed, `z-index: 0` layer (`#terrain` in
  `index.html`) filled by `terrainField()` in `js/app.js`: nested, slightly
  irregular closed rings (`wobblyRing`, never perfect circles) around a few
  peaks, plus two soft racing-line flows. Strokes use `--terrain-line` /
  `--terrain-gold`. It sits behind `main` (`z-index: 1`).
- **Topbar** — translucent warm glass (`backdrop-filter`), hairline border;
  brand mark = liquid-edged gold→copper chip with the activity glyph.
- **Tabs** — scrolling pill row; active = deep-ink pill, chrome rim, energy icon.
- **Central node (hero)** — the focus of the day view: a `min(400px,100%)`
  liquid-edged, glossy "pebble" (`--node-hi/mid/lo` radial + specular `::after`
  + **chrome/gold conic bezel**) containing the kicker, h1 session title, and
  date. Encircled by `orbitLines()` — three irregular `ellipse` orbit rings,
  orbiting node dots, and two gold racing-line arcs. Chips + pace target sit
  centered beneath it.
- **Card** — **translucent warm glass** (`backdrop-filter: blur(14px)`, chrome
  hairline border, pearl top gradient), `--radius`, `--shadow + --gloss`;
  `pad-0` removes padding for list cards. `.card-title` carries the gradient tick.
- **Week** — days ride a vertical **contour spine** (`.week-grid::before`
  gold→copper→terrain); each `.week-row` is a node with a connector stub, an
  irregular radius, and a chrome `status-dot`.
- **Calendar** — cells are **irregular pebbles** with pearl gloss; today = gold
  ring + glow; each cell carries its day kind spark plus a status spark / RPE tag.
- **Chips** — pearl pills; `.dot` for intensity, Lucide glyph for duration;
  semantic kind classes (`.z2/.z4/.z5/.spd/.test/.long/.rest/.ghost`).
- **Detail list** — recessed rows with a gold→copper bullet.
- **KB block** — dashed recess with dumbbell glyph + chrome `KB A/B/C` badge.
- **Bars / charts** — pill tracks with a recessed inset; `.bar-fill.actual` is a
  gold→copper gradient. (JS passes explicit `var(--kind)` fills for adherence.)
- **Stat** — airy, not boxed: a gold→copper rule (border-image) + Work Sans
  number + label.
- **Modal / toast** — `--radius-lg`, blurred backdrop, `rise`/`pop` motion.

---

## 8. Layout

- Max width `--maxw: 920px`, centered, generous gutters (`18px`).
- **Stacked, breathing sections** — not a dense grid of KPI cards.
- Single-column on mobile; `grid-2` / `grid-3` collapse to one column ≤ 520px.
- Safe areas respected (topbar `padding-top`, body/footer `env(safe-area-inset)`).
- No horizontal scroll except intentional `.scroll-x`.

---

## 9. Anti-patterns — do not do

- A typical fitness app: neon, black/red, aggressive angles, "beast mode".
- SaaS dashboard: dense card grids, heavy sidebars, metric walls, generic data
  tables as the primary surface — or anything that could belong to Strava, Whoop,
  Notion, or a stock component library.
- Generic radial charts, perfect geometric orbits, flat card stacks.
- Over-glossy plastic Y2K that reads dated rather than refined; heavy neon.
- Flat earthy-minimal with no digital/highlight life.
- Cool hues from outside the palette — verify a rendered screenshot has ~0%
  cool pixels (blue-dominant).
- Emoji as icons; mixed icon sets; mixed corner radii; one duration for every
  transition; animating width/height.
- Cramped density, hard rectangular boxes, text under 12px, gray-on-gray,
  sub-4.5:1 kind-chip contrast.

---

## 10. Files & how to change it

| File | Owns |
|------|------|
| `css/styles.css` | All tokens, components, motion, dark mode. **Start here.** |
| `index.html` | Font links, theme-color, favicon, `#terrain` container, static icons |
| `js/app.js` | `ICONS` + `icon()`, `orbitLines()`, `terrainField()`, semantic kinds |

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
- **2026-10-12** — Re-cut as **Orbital Contour Map**. New strict 8-color palette
  (Deep Structure / Mid Terrain / Warm Earth / Light Surface / Liquid Gold /
  Burnt Copper / Chrome / Cool Contrast); single-family Work Sans; the day hero
  is now a glossy, liquid-edged **central node** inside irregular orbit rings; a
  generated **topographic contour field** sits behind everything; week becomes a
  contour   spine of nodes; calendar cells are irregular pebbles; Lucide icons
  moved to a medium 1.75 stroke; all kind colors re-tuned to ≥ 4.5:1.
- **2026-10-12** — Pushed the "objects in a landscape" read: cards became
  translucent warm glass so the contour field shows through; the central node
  gained a conic chrome↔gold bezel and orbiting node dots; the active tab and
  status pills became chrome→gold Y2K gradients; contour/flows made more visible.
