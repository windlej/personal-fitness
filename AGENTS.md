# AGENTS.md — Training Log repo

This repo is a personal **running + kettlebell training plan** and a tiny static
web app for viewing today's session and logging how it felt. Read this file, then
`docs/training-context.md`, before making changes.

## What this is

- **Dated 12-month progression** — Oct 1 2026 → Oct 3 2027, across six phases
  (see below), with a down week roughly every 4th. Session content lives in the
  workbook's **Daily Schedule** sheet and is parsed into `data/plan.*`.
- **Lydiard conditioning + Norwegian singles** — mostly easy running, one long
  run, weekly strides, three kettlebell-only days. Two hard days a week in
  build/peak blocks; the light block has none. Dates outside the window fall
  back to a repeating sun→sat A/B template, so the app can still resolve *any*
  date.
- Hosted free on GitHub Pages (static, no build). Live at
  <https://windlej.github.io/personal-fitness/>.

> **Sheet gotcha:** the Daily Schedule's `Day` column is mislabeled — it runs one
> day ahead of the real weekday (e.g. a row dated 2026-10-04, a real Sunday, is
> labeled "Mon"). The **Date** column is correct; `build_plan.py` trusts dates
> and derives the weekday from them.

## Phases

| Phase | Dates | Shape |
|-------|-------|-------|
| 1 Re-Entry / Reset | 2026-09-30 → 2026-11-30 | 3–4 **easy** runs, no quality. Nov stays ~110–155 min/wk |
| 2 Base Build | 2026-12-01 → 2027-01-17 | All easy, volume-led (185 → 235 min/wk). Dec 13 indoor mile; Jan 17 5K TT (the sub-31 gate) |
| 3 Hills + Sharpen | 2027-01-18 → 2027-02-07 | Sub-threshold singles + hill repeats |
| 4 5-Mile Peak | 2027-02-08 → 2027-03-07 | Goal-pace threshold/VO2, taper, **St Paddy's 5 Miler** |
| 5 Bloomsday 12K | 2027-03-08 → 2027-05-02 | Rebuild + Doomsday Hill sessions, **Bloomsday 12K** |
| 6 General / Half-Marathon | 2027-05-03 → 2027-10-02 | Back to the two-quality template |

## Weekly template (build/peak weeks)

| Day | Session | Kind |
|-----|---------|------|
| Sun | Rest from running + **KB A** (hinge & press) | rest |
| Mon | **Quality 1**: sub-threshold single (RPE 5–6) or threshold | subthreshold / threshold |
| Tue | Easy Z2 + **KB B** (upper & core); strides some weeks | easy |
| Wed | **Quality 2**: hills / VO2 / flat accelerations | speed / vo2 |
| Thu | No running + **KB C** (squat, single-leg, carry) | rest |
| Fri | Easy Z2 + strides | easy |
| Sat | **Long run**, easy (75' in the 5-mile peak, up to 90' in the Bloomsday block) | long |

Kettlebell days are Sun (A), Tue (B), Thu (C). Wednesday has **no** kettlebell.
**Sub-threshold singles (`kind: subthreshold`, zone Z3) are MODERATE, not hard** —
they do not count toward the two-quality-days-per-week budget. Race/taper weeks
drop the long run and all quality.

## File map

- `index.html`, `css/styles.css`, `js/app.js` — the web app. `js/app.js` resolves
  any date to a session (dated schedule first, then the A/B fallback), handles
  logging (localStorage), export/import, and a **critical-speed pace engine**
  (header **Paces** modal: race efforts + max HR → per-workout pace & HR, stored
  in localStorage). **Edit here only for app/UI changes.**
- `data/plan.js` / `data/plan.json` — **generated** plan data (`window.PLAN`):
  `meta`, the dated `schedule` (keyed by ISO date), `weeks`, `phases`, the
  out-of-range `template` (A/B), and `zones`. **Never hand-edit** — regenerate.
- `scripts/build_plan.py` — the source of truth. It **parses the workbook's
  `Daily Schedule`** (dates, sessions, run minutes, intensity, details, KB work,
  notes) into `schedule`/`weeks`/`phases`, reads zones/paces from
  `Zones & Sessions`, and keeps an A/B `build_week()` template as the
  out-of-range fallback. **Edit session content in the workbook; edit the
  fallback template / parsing here.**
- `docs/training-principles.md` — the athlete's **authoritative training
  philosophy**. Loaded into every session via `opencode.json` `instructions`;
  the coach follows it over generic advice. Edit it to change how the coach
  thinks, not just what it knows.
- `docs/training-context.md` — the athlete's goals, constraints, and preferences.
  Update this when life changes; the coach reads it.
- `docs/how-to-use.md` — plain-language usage guide for the app + coach.
- `docs/design-system.md` — the **living visual design system** (palette, tokens,
  type, motion, components, anti-patterns). Update it alongside any change to
  `css/styles.css`. Edit `css/styles.css`/`index.html`/`js/app.js` for the look;
  this doc is the reference.
- `scripts/build_history.py` — distills a Strava/SmashRun CSV export into
  `docs/training-history.md` (coach-readable history/insights) and
  `data/history-summary.json`. Output is **generated and git-ignored** (personal).
- `.opencode/` — opencode agent + skill config (see below).

## Rebuild + deploy

```bash
python3 -m pip install openpyxl      # once
python3 scripts/build_plan.py        # regenerates data/plan.js + data/plan.json
```

Then commit on `main` and push; GitHub Pages redeploys automatically.

## Logging data

Logs live in the browser's `localStorage` (private, per-device). To let the
coach read them, export **JSON** from the app's **Data** view and save it as
`journal-export.json` in the repo root. **This file is git-ignored and must
never be committed — the repo is public.**

## opencode config in this repo

- **Agent** `.opencode/agent/training-coach.md` — "training-coach" persona
  (primary mode). Switch to it with the agent picker.
- **Skill** `.opencode/skills/modify-training-plan/SKILL.md` — the safe workflow
  for changing the template, zones, or adding a race/goal.
- Config loads once at startup: **restart opencode after editing any of these.**
