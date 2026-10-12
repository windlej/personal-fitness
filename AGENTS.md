# AGENTS.md — Training Log repo

This repo is a personal **running + kettlebell training plan** and a tiny static
web app for viewing today's session and logging how it felt. Read this file, then
`docs/training-context.md`, before making changes.

## What this is

- **Continuous weekly template** — a repeating **Sun → Sat** week that never
  ends. Weeks alternate **A** and **B** by week parity (no phases, no dated
  calendar). Any date resolves to a session.
- **80/20-ish polarized** toward easy running, with two quality days, one long
  run, three kettlebell-only days, and strides.
- Hosted free on GitHub Pages (static, no build). Live at
  <https://windlej.github.io/personal-fitness/>.

## Weekly template (authoritative)

| Day | Session | Kind |
|-----|---------|------|
| Sun | Rest from running + **KB A** (hinge & press) | rest |
| Mon | **Quality 1: Threshold** (3×8') | threshold |
| Tue | Easy Z2 + **KB B** (upper & core); strides on A weeks | easy |
| Wed | **Quality 2**: VO2 5×3' (A weeks) / hill sprints (B weeks) | vo2 / speed |
| Thu | No running + **KB C** (squat, single-leg, carry) | rest |
| Fri | Easy Z2 + strides | easy |
| Sat | **Long run** (80') | long |

Kettlebell days are Sun (A), Tue (B), Thu (C). Wednesday has **no** kettlebell.

## File map

- `index.html`, `css/styles.css`, `js/app.js` — the web app. `js/app.js` derives
  any date's session from the template, handles logging (localStorage), and
  export/import. **Edit here only for app/UI changes.**
- `data/plan.js` / `data/plan.json` — **generated** plan data (`window.PLAN`).
  **Never hand-edit** — regenerate with `scripts/build_plan.py`.
- `scripts/build_plan.py` — the source of truth for session content and volume.
  Zones/paces are read from `Training Plan (1).xlsx`; sessions are defined in
  `build_week()`. **Edit the template here.**
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
