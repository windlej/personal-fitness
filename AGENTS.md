# AGENTS.md — Training Log repo

This repo is a personal **running + kettlebell training plan** and a tiny static
web app for viewing today's session and logging how it felt. Read this file, then
`docs/training-context.md`, before making changes.

## What this is

- **Dated 12-month progression** — Oct 1 2026 → Oct 3 2027, across six phases,
  with a down week roughly every 4th. Session content lives in the workbook's
  **Daily Schedule** sheet and is parsed into `data/plan.*`.
- **80/20-ish polarized** toward easy running, with two quality days, one long
  run, three kettlebell-only days, and strides. Dates outside the window fall
  back to a repeating sun→sat A/B template, so the app can still resolve *any*
  date.
- Hosted free on GitHub Pages (static, no build). Live at
  <https://windlej.github.io/personal-fitness/>.

> **Sheet gotcha:** the Daily Schedule's `Day` column is mislabeled — it runs one
> day ahead of the real weekday (e.g. a row dated 2026-10-04, a real Sunday, is
> labeled "Mon"). The **Date** column is correct; `build_plan.py` trusts dates
> and derives the weekday from them.

## Weekly template (build weeks)

| Day | Session | Kind |
|-----|---------|------|
| Sun | Rest from running + **KB A** (hinge & press) | rest |
| Mon | **Quality 1: Threshold** (progresses: 3×5' → 3×6' → 2×10' → 20–25' tempo) | threshold |
| Tue | Easy Z2 + **KB B** (upper & core); strides some weeks | easy |
| Wed | **Quality 2**: VO2 / hill sprints / flat accelerations | vo2 / speed |
| Thu | No running + **KB C** (squat, single-leg, carry) | rest |
| Fri | Easy Z2 + strides | easy |
| Sat | **Long run**, easy (ramps to 90') | long |

Kettlebell days are Sun (A), Tue (B), Thu (C). Wednesday has **no** kettlebell.
Maintenance weeks (Nov–Dec) drop to one quality day; holiday/race weeks go light.

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
