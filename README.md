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
- **Paces** (header) — enter race/time-trial results and max HR; the app derives target pace **and HR** for each workout from your critical-speed model.
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
Effort/RPE always wins over the watch on hot, hilly, or tired days.

---

## Training paces

Open **Paces** in the header and enter your max heart rate, an **AeC %**
(anaerobic-capacity fraction, default 12%), and one or more all-out efforts (a
race or time trial: distance, time, date). From those the app derives your target
**pace range and HR** for every workout.

**Two or more efforts** — critical-speed model:

```
CS   = (d₂ − d₁) / (t₂ − t₁)          critical speed (m/s)
D'   = d_small − CS · t_small          anaerobic distance capacity (m)
vVO₂ = min( CS + D' / 425.5 , Riegel 6-min pace from the shorter race )
```

**One effort** — single-race model:

```
P_race    = time / distance × 1609        (sec/mi of the effort)
CP pace   = P_race / (1 − AeC/2)
vVO₂ pace = 2·P_race − CP pace
CS = CP speed, vVO₂ = vVO₂ speed
```

**Zone speeds** (either model), as fractions of vVO₂ — tuned so easy/recovery
lands where it should rather than far too slow:

```
LT2 = (1 − 1.5·AeC)·vVO₂     LT1 = (1 − 1.9·AeC)·vVO₂
FatMax = (1 − 2.4·AeC)·vVO₂
BZ2 = (1 − 2.75·AeC)·vVO₂    BZ1 = (1 − 3.55·AeC)·vVO₂
```

At the 12% default that's LT2 0.82, LT1 0.772, FatMax 0.712, BZ2 0.67, BZ1 0.574
of vVO₂.

The app lists the full anchor ladder — **vVO2 Max → Critical Power → LT2 / MLSS →
LT1 / AeT → FatMax → Bottom of Zone 2 → Bottom of Zone 1** — with a pace and HR for
each, then the zone ranges. Zones: `Z2 = BZ2→LT1` (easy, long), `Z4 = LT2→CS`
(threshold), `Z5 = CS→vVO₂` (VO2), `Z6` faster than vVO₂ (sprints). HR targets
scale from %maxHR (vVO₂ 100, CS 93, LT2 88, LT1 83, FatMax 78, BZ2 73, BZ1 60).
Lower **AeC = better aerobic fitness** (~6.5–7% elite, up to ~15% newer runners).
Efforts, AeC, and max HR are stored in this browser only and included in your
JSON export.

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
