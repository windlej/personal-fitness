# Design system — "Terminal"

**Living document.** This is the source of truth for how the app looks, feels,
and moves. When you change the design, change this file too. The implemented
tokens live in `css/styles.css` (`:root`); everything below mirrors them. The
component vocabulary is built in `js/app.js` (`section()`, `facts()`, `table()`,
`kindToken()`, `barMarkup()`, `columnChart()`, `figure()`), and the static
shell is `index.html`.

> Changing the plan content is a different job — see
> `.opencode/skills/modify-training-plan/SKILL.md`. This doc is about the visual
> language only.

---

## 1. Core feeling

**A useful session manual, rendered as a terminal.** One continuous black page in
green IBM Plex Mono, arranged as **commands and their output**. Every view is a
stack of numbered commands — `01 today`, `02 session`, `03 steps` — with a
character-aligned command gutter beside a wider output column. Thin green rules
separate commands; white is strong emphasis; a small ANSI palette marks real
session and status semantics.

The identity is a **character wordmark** (`TLOG`, derived from "Training Log")
plus the real name, the current date, and the week/phase that frames the page.

**It is not** a shell emulator: there is no prompt, no typed input, no fake
logs, no invented file paths, flags, statuses, or metrics. Every
command-shaped control is a real button or link that does the real thing. The
labels name content (`01 week`, `02 days`, `03 markers`), they do not claim
functionality the app lacks.

**Mobile first.** The phone layout is the default: one column, label above
output, output indented two characters. Desktop only widens the gutter and moves
output to the right.

---

## 2. Palette (13 colours, ANSI/neofetch style)

The page chrome is green and white. Accents are **only** for semantic
session/status data — never borders, page furniture, or decorative headings.
No colored backgrounds except reverse video for selection.

| Token | Hex | Role |
|-------|-----|------|
| `--dp-color-ground` | `#000000` | Page ground |
| `--dp-color-ink` | `#66ff66` | Primary green: chrome, labels, active |
| `--dp-color-ink-muted` | `#58ca58` | Supporting text |
| `--dp-color-rule` | `#255325` | Quiet rules and separators |
| `--dp-color-emphasis` | `#ffffff` | Strong emphasis, selected text |
| `--dp-color-dim` | `#8a8a8a` | Rest, disabled, tertiary |
| `--dp-color-cyan` | `#5fd7ff` | Easy / Z2, informational |
| `--dp-color-blue` | `#5f87ff` | Long run |
| `--dp-color-teal` | `#5fd7af` | Sub-threshold / Z3 |
| `--dp-color-yellow` | `#ffd75f` | Threshold / Z4 |
| `--dp-color-orange` | `#ff875f` | VO2 / Z5 |
| `--dp-color-magenta` | `#d787ff` | Speed / strides |
| `--dp-color-red` | `#ff5f5f` | Race / test / skipped |

No `color-mix`, no `rgba`, no gradients, no second hue. `transparent` is the only
other value used. Form controls borrow `--dp-color-dim` through
`--dp-control-border` because their 1px boundary is the only thing showing the
hit area: it measures 6.08:1 against black, where `--dp-color-rule` (the quiet
separator, 2.34:1) would fail WCAG 1.4.11. That keeps the count at 13 colours —
no fourteenth token was added.

### Session-kind mapping

| Kind | Token | Class | Prefix |
|------|-------|-------|--------|
| easy / Z2 | `[Z2]` cyan | `.tok--easy` | — |
| long | `[LONG]` blue | `.tok--long` | — |
| sub-threshold / Z3 | `[Z3]` teal | `.tok--z3` | — |
| threshold / Z4 | `[Z4]` yellow | `.tok--z4` | — |
| VO2 / Z5 | `[Z5]` orange | `.tok--z5` | — |
| speed / strides | `[SPD]` magenta | `.tok--spd` | `>>` |
| race / test | `[RACE]` red (title white) | `.tok--race` | `!!` |
| rest | `[REST]` dim | `.tok--rest` | — |
| kettlebell | `[KB A/B/C]` green | `.tok--kb` | — |

Status tokens: `[DONE]` green, `[MODIFIED]` yellow, `[SKIPPED]` red,
`[ ]` dim. Calendar also uses `[x]`, `[~]`, `[!]`.

`js/app.js` owns the mapping (`KIND`, `ZONE_CLS`, `STATUS_TEXT`, `CAL_KIND`);
keep token text and class names in sync when adding a kind. Colour is never the
only signal — every token carries a bracketed word or symbol plus a legend.

---

## 3. Typography

- **One family:** IBM Plex Mono, loaded from Google Fonts via `@font-face` in
  `css/styles.css` and bound to the CSS family name **`TerminalPlex`**
  (`--dp-typography-face: "TerminalPlex", monospace`), weights 400 and 500.
- All text, controls, and numbers are monospaced. No second family, no serif, no
  sans fallback as a design choice.
- Body `18px`, phone `clamp(16px, 4.2vw, 18px)`; labels `16px`; support text
  `14px` (`--dp-typography-small`, used by nav labels at ≥900px, every meta line
  and caption); headings `24px`; display `40px` (session title) with
  `--dp-typography-display-narrow: 32px` below 900px.
- Leading: body/list `1.5` (`--dp-typography-list-leading: 27px`), display `1.2`
  (`1.25` narrow).
- Emphasis comes from **weight, white, punctuation, and indentation** — not from
  a second font or oversized type.
- Inputs are `16px` minimum so iOS does not zoom on focus. Nothing essential is
  below `14px`.

---

## 4. Space, rules, and shape

- **Characters, not pixels, define horizontal rhythm:** `1ch` cell, `2ch`
  gutter (phone indent), `3ch` column gap, `4ch` wide column gap.
- Vertical rhythm: `9px` inset, `18px` compact row, `27px` row, `36px` compact
  section, `54px` section.
- **Rules:** one hairline (`1px`) in `--dp-color-rule` separates commands, fact
  rows, table rows, bar groups, and the menu. No card backgrounds, no shadows,
  no gradients, no blur, no texture, no CRT curvature.
- **Shape:** `--dp-radius-control: 0`. Every field, button, cell, panel, and
  modal is square. No pills.
- Layout measure: content `94ch` max (`18ch` gutter + `4ch` gap + `72ch` output
  on desktop), centered.
- Safe areas: `env(safe-area-inset-*)` on masthead, modal header, toast, footer.

---

## 5. Layout

### Shell

1. **Masthead** — character wordmark (`TLOG`, ASCII, `aria-hidden`), the real
   name `training log` as the `h1`, a single blinking cursor, and two fact lines
   (date, current week/phase). Not sticky.
2. **Menu** — eight real targets in one `nav` with a numbered gutter:
   `01 today  02 week  03 calendar  04 journal  05 progress  06 plan
   07 paces  08 data`. Phone/tablet: two columns, four rows, each ≥44px tall.
   Desktop (≥900px): one row, sticky, 14px labels.
   Active view: reverse video plus `aria-current="page"`.
   `paces` and `data` are real buttons that open their dialogs.
3. **`main#app`** — the current view, built from commands.
4. **Footer** — a directory-style list of real facts (storage, backup, schedule)
   with a real `[open data]` button.

### Command gutter

Every section is:

```html
<section class="cmd">
  <h2 class="cmd-label"><span class="cmd-num">01</span>today</h2>
  <div class="cmd-out">…output…</div>
</section>
```

- **Desktop (≥900px):** `18ch | minmax(0, 72ch)`, gap `4ch`.
- **Tablet (540–899px):** `14ch | 1fr`, gap `3ch`. The gutter fits the longest
  label (`02 kettlebell`), so labels never break mid-word.
- **Phone (<540px):** one column; the label sits above its output and the output
  is indented `2ch` (calendar opts out with `.cmd--flush`).
- The first command has no top rule (the menu's bottom rule is the separator).
- Gap between commands (`27px` padding + rule) is larger than the gap between
  lines of output.

### Output patterns in use

- **Aligned fact rows** — `dt` 12ch (`10ch` at tablet) + value: session facts,
  progress totals, footer directory.
- **Numbered steps** — `01` gutter + instruction, for a session's warm-up /
  main set / cool-down.
- **`-` line lists** — kettlebell sets.
- **`>` quoted statements** — the plan goal and per-session notes.
- **Comparison tables** — phases, the 53-week schedule, anchors, zones. On a
  phone each row becomes stacked `label value` lines via `td::before`
  (`data-k`); no horizontal scrolling.
- **Figures** — one chart vocabulary, three primitives, all drawn from
  `store.logs` / `PLAN`:
  - **Bullet bar** — `[#####|...]`, 10 cells. Fill = value, `|` = target,
    dim dots = the rest. Used for completion / split / adherence and the
    12-week volume rows (fill = logged, `|` = planned).
  - **Column plot** — `<pre class="chart">` with a 3ch axis, `|` spine, `+`
    origin, `---` baseline and one-character columns at 2-cell pitch. Week
    load uses filled columns whose character is the real status
    (`# done`, `+ modified`, `! skipped`, `: planned`); the RPE trend uses
    `dots: true` so each session is a single mark at its value.
  - **Figure wrapper** — `<figure>` + `figcaption` (window/units) + plot
    (`aria-hidden`) + one-line note (legend/summary). The caption and note are
    the text alternative.
  - Rules: zero baseline; round the scale up to a friendly minute step; no
    figure under three data points; ASCII glyphs only; one figure per idea.
- **Tables with a figure column** — the phases table carries a load bullet per
  phase (`Planned load`), so a comparison table can visualise one column
  without a second, redundant chart.

---

## 6. Components

- **Day navigator** — `[<]` date input `[>]`, weekday + week beneath, and a real
  `[jump to today]` when off today.
- **Session panel** — display-size white session title, then an aligned fact
  table: DATE, WEEK, TYPE (token + kind word), TIME, INTENSITY, PACE, STATUS.
  The masthead and the DATE row already say "today", so there is no kicker.
- **Kettlebell block** — a `1px` bordered section headed by `[KB A]` + real name,
  with `-` set lines. No background.
- **Log form** — status buttons show `[ ]`/`[x]` + label and `aria-pressed`;
  selected states are reverse video in the status colour. Duration, distance,
  RPE range (with `<output>` and hint), feel, notes. Save is a filled green
  control; Clear is red-outlined.
- **Week** — the load figure (7 planned-minute columns, status characters,
  `S M T W T F S` labels) above one row per day: `DOW DATE` | token + session +
  metadata | status token. Phone stacks the session and tags under the date
  line.
- **Calendar** — 7 equal columns at 320px, cells ≥56px tall. Each cell is a
  button: day number, a bracketed kind character (`[2] [L] [3] [4] [5] [S] [R]
  [·]`), and a status mark (`[ ] [x] [~] [!]`). A two-line legend explains both,
  so colour is never the only signal. Today gets a white border.
- **Journal** — monospaced log lines as real buttons: date, session, kind and
  status tokens, then RPE · time · distance · pace · feel and a `-` note.
- **Progress** — totals as fact rows with a real 10-character completion bar,
  a completed/skipped/not-logged split, the 12-week volume bullets (logged
  fill, planned tick), the RPE dot plot, and adherence by session type.
- **Plan** — title, `>` goal quote, phases table (with a load bullet per
  phase), full week-by-week schedule, then either the computed anchor/zone
  tables or the static zone reference.
- **Dialogs** — full-screen on phone with a sticky header and scrollable body;
  centered square panel on desktop. Real actions: export/import JSON, export
  CSV, unit select, erase, add/remove effort, save paces. Close is `[x]`
  (`aria-label="Close"`); Escape closes; Tab is trapped; focus returns to the
  opener.
- **Toast** — a single bottom status line prefixed with `>`, `role="status"`,
  safe-area aware.
- **Controls** — rectangular, flat, monospaced. Default: rule border + green
  text. Hover: inversion or underline. Focus: `2px` white outline, `2px` offset.
  Tap targets ≥44px.

There is no icon system: functional glyphs are text (`[<]`, `[>]`, `[x]`, `[+]`,
`[open data]`), with accessible names where the glyph alone is ambiguous.

---

## 7. Motion

- **One animation:** the masthead cursor blinks at `--dp-motion-cursor` (1.2s)
  with discrete steps.
- `prefers-reduced-motion: reduce` stops the blink; the cursor stays solid.
- Everything else is still and immediate: no rise, hover lift, modal pop,
  transitions, gradient shifts, or background motion. Nothing types itself out
  and no invented log streams play.

---

## 8. Accessibility

- Real `button` / `input` / `select` / `textarea` / `a` elements with accessible
  names; the command labels are real `h2`s, session title an `h3`.
- Reading order equals DOM order; the skip link reaches `main#app`
  (`tabindex="-1"`).
- `aria-current="page"` on the active view, `aria-pressed` on status buttons,
  `aria-label` on calendar cells (date, session, kind, status, RPE), `role="status"`
  on the toast, `aria-labelledby` on the dialog.
- Focus is always visible (white outline). Dialogs trap Tab and restore focus.
- ASCII art (wordmark, RPE chart) is `aria-hidden="true"`; the real text version
  is adjacent or in the chart note.
- Accents were checked for contrast against black; body green/white is well above
  4.5:1.
- No information is hover-only.
- **Re-renders keep focus.** Views are template strings written into `#app`, so
  `captureFocus()` records a stable selector (`#id`, `data-action`, `data-status`,
  `data-date`) before the write and `restoreFocus()` re-focuses it after. If the
  control no longer exists (a view switch), focus moves to `main#app` instead of
  falling to `<body>`.
- `data/plan.js` failing to load renders a one-line message in `#app` rather than
  a blank page.

---

## 9. Anti-patterns — do not do

- Fake shell prompts, commands, logs, file paths, flags, statuses, or metrics.
- Gradients, glow, gloss, backdrop blur, textures, CRT curvature, scan lines.
- Rounded cards, pills, chips with backgrounds, colored page furniture.
- Lucide/SVG icon sets, emoji icons, mixed families.
- Colour as the only signal; accent colour on borders or headings.
- Animating typing, layout, or invented output.
- Horizontal scrolling at any width; ASCII art that doesn't fit 320px.
- Tables that require sideways scrolling on a phone.

---

## 10. Files & how to change it

| File | Owns |
|------|------|
| `css/styles.css` | Tokens, `@font-face`, commands, components, motion, reduced motion. **Start here.** |
| `index.html` | Wordmark, masthead, menu, footer, dialog shell, toast, theme colour. |
| `js/app.js` | View markup helpers (`section`, `facts`, `table`, `kindToken`) and the chart vocabulary (`barModel`, `barMarkup`, `columnChart`, `figure`); the wordmark is static in HTML. |

**Workflow for a visual change:** edit the token in `css/styles.css`; every
component follows. Update the tables above if a token value changes. Re-check
320 / 540 / 800 / 1100 / 1440 and a keyboard pass. Quick visual QA (no build):

```bash
# renders each view; headless Chrome, no install
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
"$CHROME" --headless=new --hide-scrollbars --window-size=1100,1500 \
  --virtual-time-budget=5000 --screenshot=/tmp/day.png \
  "file://$PWD/index.html#day"
```

Headless Chrome clamps its window to a minimum width, so true 320px shots need
the page loaded inside a fixed-width iframe (or device emulation).

---

## Changelog

- **2026-10-12** — Initial chilled Y2K × Nature system (Work Sans, Lucide,
  light/dark).
- **2026-10-12** — Re-cut as **Orbital Contour Map** (8-colour palette, glossy
  central node, contour field, orbit rings).
- **2026-11-07** — Re-cut as **Terminal**. Dark only (single black theme), IBM
  Plex Mono everywhere, 13-colour ANSI palette used only for session/status
  semantics, numbered command gutter, character-aligned rows and tables,
  10-character bars, ASCII wordmark and RPE chart, square corners, no gradients,
  blur, glow, pills, or icons. Removed the terrain field, orbit rings, glossy
  node, Lucide system, and the light theme. Logging, exports, imports, unit
  switch, and the critical-speed pace engine are unchanged.
- **2026-11-07** — Hardening pass after an accessibility/UX audit: focus is
  restored by selector across in-place re-renders (day steps, status, save,
  month nav) and moves to `main` on view switches; journal RPE/distance values
  are escaped; the unit switch repaints immediately; form controls use a 6.08:1
  border token; `--dp-typography-small` replaces 27 literals; dropped the
  duplicate `today` kicker and the duplicate empty status token; added a plan
  data guard and a font preconnect.
- **2026-11-07** — Data figures. One chart grammar (`barModel`, `barMarkup`,
  `columnChart`, `figure`): bullet bars with a planned tick, a `<pre>` column
  plot with a real axis and zero baseline, and a caption/note wrapper. Added
  the Week load chart, 12-week volume bullets (replacing the old bar rows), an
  RPE dot plot, and a per-phase load column in the Plan table. Captions carry
  the window and units; every plot is `aria-hidden` with a text alternative.
