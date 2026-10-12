# Training Log — 12-Month Run + Kettlebell Plan

A tiny, dependency-free web app that shows **today's workout** from a dated
12-month training progression, lets you **log RPE / distance / notes** afterwards, and
**exports your journal** as JSON or CSV. It runs entirely in the browser and is
hosted for free on GitHub Pages.

- **Today view** — opens on today's session (intensity, run time, details, kettlebell block, notes) plus the RPE log form.
- **Week / Calendar** — any date, past or future; colour-coded by intensity.
- **Journal** — every logged session in one list.
- **Progress** — completion %, time/distance logged, weekly planned-vs-logged volume, RPE trend, adherence by session type.
- **Plan** — the phases, the full 12-month week-by-week schedule, and zones & paces.
- **Data** — export/import JSON (backup / move devices) and export CSV.

No build step, no frameworks, no accounts. Your logs live in this browser's
`localStorage`, so **export regularly**.

> **New here? Read [`docs/how-to-use.md`](docs/how-to-use.md)** — a plain-language
> guide to the daily flow, backups, and using the AI training coach.

---

## The training plan

A **dated 12-month progression** (Oct 2026 → Oct 2027) across six phases, with a
down week roughly every 4th. Session content lives in the workbook's
**Daily Schedule** sheet; the app shows the exact session for any date in the
window. Dates outside the window fall back to a repeating Sun → Sat template.

| Day | Session |
|-----|---------|
| **Sun** | Rest from running + **KB A** (hinge & press) |
| **Mon** | Quality 1: **Threshold** (progresses over the plan) |
| **Tue** | Easy Zone 2 (+ strides some weeks) + **KB B** (upper & core) |
| **Wed** | Quality 2: **VO2 Max** or **Sprints/Strides** — no kettlebell |
| **Thu** | No running + **KB C** (squat / single-leg / carry) |
| **Fri** | Easy Zone 2 + strides |
| **Sat** | **Long run**, easy (ramps up over the plan) |

Maintenance weeks (Nov–Dec) drop to one quality day; holiday/race weeks go light.
Paces come from the 20-min time-trial reference. Effort/RPE always wins over the
watch on hot, hilly, or tired days.

---

## Repo layout

```
index.html              # app shell
css/styles.css          # styling (light + dark)
js/app.js               # all app logic (resolves any date's session)
data/plan.js            # generated: dated schedule + phases + zones
data/plan.json          # same data as JSON
scripts/build_plan.py   # parses the workbook's Daily Schedule into data/plan.*
scripts/build_history.py# distills a Strava/SmashRun CSV into a history digest
docs/                   # how-to-use.md, training-context.md (+ personal history)
Training Plan (1).xlsx  # original source workbook (source of session content)
```

`data/plan.js` / `data/plan.json` are **generated** — don't hand-edit them.
Edit session content in the workbook (or the zones), then rebuild.

---

## Local preview

```bash
python3 -m http.server 8000
# open http://localhost:8000
```

## Rebuild the data

```bash
python3 -m pip install openpyxl
python3 scripts/build_plan.py
```

---

## Deploy on GitHub Pages (free)

This repo is already set up as a static site (no build step):

1. Push to GitHub (`main`).
2. Repo → **Settings → Pages → Source: "Deploy from a branch"**.
3. Branch **main**, folder **/(root)** → Save.
4. Live at `https://<username>.github.io/<repo>/`.

Add the site to your phone's home screen for one-tap access.

---

## How logging works

- Logs are keyed by date (`YYYY-MM-DD`) in `localStorage` under `tp.logs.v1`.
- Each entry: `status` (completed / modified / skipped), `duration`, `distance`,
  `rpe` (1–10), `feel`, `notes`.
- **Data → Export JSON** is a full backup. **Import / restore JSON** merges it
  back (imported dates override). **Export CSV** opens in Excel / Sheets.

---

## Coaching with opencode

This repo ships an opencode **training-coach** agent and supporting docs:

- `docs/training-principles.md` — **your authoritative training philosophy.** This
  is how you "teach" the coach the rules to follow; it's loaded into every
  session. Edit it to change how the coach thinks.
- `docs/training-context.md` — **your** goals, races, constraints, injuries. Edit
  this when life changes; the coach reads it every session.
- `.opencode/agent/training-coach.md` — the coach persona. Switch to it with the
  agent picker.
- `.opencode/skills/modify-training-plan/SKILL.md` — the safe workflow for
  changing the template, zones, or adding a race.
- `AGENTS.md` — repo/plan context loaded automatically.

To have the coach review your actual training, export **JSON** from the app's
**Data** view and save it as `journal-export.json` in the repo root (git-ignored).
For long-term context, feed it your history:

```bash
python3 scripts/build_history.py history.csv   # from a Strava/SmashRun export
```

This writes `docs/training-history.md` (volume, consistency, PBs, yearly trends)
for the coach to read. See `docs/how-to-use.md` for how to get the CSV. Restart
opencode after editing any `.opencode/` or `opencode.json` file.

## Roadmap

- [ ] Import actuals from Strava / Garmin / Apple Health (GPX/CSV or API).
- [ ] Compute pace zones from a real 20-min time trial entry instead of the placeholder.
- [ ] Training-load model (RPE × duration, acute:chronic ratio) and fatigue warnings.
- [ ] Per-day template editing in the UI (no code changes).
- [x] Drive edits and coaching via opencode with a repo-scoped "training coach" agent.
- [x] Distill Strava/SmashRun history into a coach-readable digest.
