# Training Log — 12-Month Run + Kettlebell Plan

A tiny, dependency-free web app that shows **today's workout** from your training
plan, lets you **log RPE / distance / notes** afterwards, and **exports your
journal** as JSON or CSV. It runs entirely in the browser and is hosted for free
on GitHub Pages.

- **Today view** — opens on today's session (intensity, run time, details, kettlebell block, notes).
- **Week / Calendar** — navigate any day in the 12-month plan; colour-coded by intensity.
- **Journal** — every logged session in one list.
- **Progress** — completion %, time/distance logged, weekly planned-vs-logged volume, RPE trend, adherence by session type.
- **Plan** — zones & paces, weekly rotation, phases, kettlebell progression.
- **Data** — export/import JSON (backup / move devices) and export CSV.

No build step, no frameworks, no accounts. Your logs live in this browser's
`localStorage`, so **export regularly**.

---

## Repo layout

```
index.html              # app shell
css/styles.css          # styling (light + dark)
js/app.js               # all app logic
data/plan.js            # generated from the workbook (source of truth = the .xlsx)
data/plan.json          # same data as JSON (handy for scripts/other tools)
scripts/build_plan.py   # parses "Training Plan (1).xlsx" -> data/plan.js
Training Plan (1).xlsx  # your plan
```

`data/plan.js` and `data/plan.json` are **generated** — don't hand-edit them.
Edit the workbook, then rebuild (below).

---

## Local preview

Any static server works:

```bash
python3 -m http.server 8000
# open http://localhost:8000
```

## Rebuild the data from the workbook

```bash
python3 -m pip install openpyxl
python3 scripts/build_plan.py
```

> **Note on dates:** the `Daily Schedule` sheet stores dates **one day earlier**
> than the weekday it prints (a bug in how the workbook was generated). Phase 1
> is documented as starting Thu Oct 1 2026 and the first quality session as Tue
> Oct 6 2026, so the parser shifts daily dates forward by one day to match the
> weekday labels. Weekly Summary dates were already correct.

---

## Deploy on GitHub Pages (free)

This repo is already set up as a static site (no build step):

1. Push this repo to GitHub (`main` branch).
2. Repo → **Settings → Pages → Build and deployment → Source: "Deploy from a branch"**.
3. Branch: **main**, folder: **/(root)** → Save.
4. After ~1 minute the site is live at `https://<username>.github.io/<repo>/`.

Add the site to your phone's home screen for one-tap access.

> Prefer the `.xlsx` to stay the source of truth and auto-rebuild on push? Add a
> GitHub Actions workflow that runs `scripts/build_plan.py` and deploys via
> `actions/deploy-pages`, then set Pages → Source to "GitHub Actions".

---

## How logging works

- Logs are keyed by date (`YYYY-MM-DD`) in `localStorage` under `tp.logs.v1`.
- Each entry: `status` (completed / modified / skipped), `duration`, `distance`,
  `rpe` (1–10), `feel`, `notes`.
- **Data → Export JSON** is a full backup. **Import / restore JSON** merges it
  back (imported dates override). **Export CSV** opens in Excel / Sheets.

---

## Roadmap (growing into an athlete-intelligence platform)

- [ ] Import actuals from Strava / Garmin / Apple Health (GPX/CSV or API).
- [ ] Auto-compute pace zones from the real 20-min time trial (Feb) instead of the placeholder.
- [ ] Training-load model (RPE × duration, acute:chronic ratio) and fatigue warnings.
- [ ] Race/periodization editor (add races, shift blocks) stored as a plan *overlay*.
- [ ] Drive edits and coaching via opencode with a repo-scoped "training coach" agent.

Because everything is static + `localStorage`, later features slot in without a
backend. If cross-device sync is wanted, GitHub-commit sync or a small serverless
function can be added.
