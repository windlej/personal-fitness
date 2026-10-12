# How to use your training log

A one-page guide for the athlete (and anyone else who opens this repo). For how
the plan itself is built and deployed, see the top-level `README.md`.

## Open it

- **On your phone:** open <https://windlej.github.io/personal-fitness/> in Safari
  or Chrome, then **Add to Home Screen** so it opens full-screen like an app.
- **On your computer:** same URL in any browser.
- No login, no account. Your logs are saved in **this browser only**.

## Your daily flow

1. Open the app — it lands on **Today** with the session for the current date.
2. Do the session shown (running, kettlebell, or rest).
3. Come back and fill in the log:
   - **Status** — `Done`, `Modified`, or `Skipped`.
   - **Duration** (minutes), **Distance** (optional), **RPE** (effort 1–10),
     **Feel** (how you felt), and **Notes**.
   - Tap **Save**.
4. That's it — the entry shows up in **Journal** and counts toward **Progress**.

> Tip: log honestly. RPE and "feel" are what make the coach's feedback useful.

## The views

| View | What it's for |
|------|----------------|
| **Today** | The session for today + the log form. |
| **Week** | This week's Sun→Sat layout with your logged status. |
| **Calendar** | Any date, past or future (colour-coded by intensity). |
| **Journal** | Every session you've logged, newest first. |
| **Progress** | Completion %, time/distance logged, planned-vs-logged volume, RPE trend, adherence by session type. |
| **Plan** | The weekly template and the zone/pace table. |
| **Data** | Export/import your logs. |

## Back up your data (important)

Logs live only in the browser's `localStorage`. Clearing your browser data, or
switching devices, means starting over — so **export regularly**:

- **Data → Export JSON** — full backup. Save it somewhere safe. This is also the
  file to hand to the coach (see below).
- **Data → Import / restore JSON** — merges a backup back in (imported dates win).
- **Data → Export CSV** — opens in Excel / Google Sheets.

## Using the AI training coach

This repo includes an opencode **training-coach** agent (see `README.md` and
`AGENTS.md`). To use it:

1. **Fill in `docs/training-context.md`** — your goals, races, constraints,
   injuries, equipment. The coach reads this first.
2. **Give it your data:** in the app, **Data → Export JSON**, then save the file
   as `journal-export.json` in the repo root. (It's git-ignored — never
   committed, because this repo is public.)
3. **Restart opencode**, then switch to the **training-coach** agent with the
   agent picker (press `Tab`).
4. Ask things like:
   - "How was my week? Anything to adjust?"
   - "I'm doing a 10K in 8 weeks — adjust the template."
   - "My Tuesday runs feel too hard lately."

The coach edits the plan by following the
`.opencode/skills/modify-training-plan/SKILL.md` workflow, then rebuilds and
shows you the diff before committing.

## Leverage your Strava / SmashRun history

You have years of real training data — use it to spot **consistency, trends, and
what you've actually sustained**, so the coach can ground its advice.

1. **Get a CSV export:**
   - **Strava:** Settings → My Account → *Download your account* → Request
     download. The emailed zip contains `activities.csv`.
   - **SmashRun:** open `smashrun.com/<your-username>/export` (or Account
     Settings → *Request Bulk Export*).
2. **Save it** in the repo root as `history.csv` (git-ignored).
3. **Run the digest:**
   ```bash
   python3 scripts/build_history.py history.csv
   ```
   This writes `docs/training-history.md` — all-time volume, consistency and
   streaks, personal bests, yearly trends, and insight notes — plus a
   machine-readable `data/history-summary.json`.
4. **Ask the coach** about it: "Given my 10-year history, is my current weekly
   volume realistic?" or "Where do I lose consistency?"

Both generated files are git-ignored. If the CSV columns aren't detected, the
script prints the headers it saw — pass `--unit km|mi|m` or rename the columns.

## Privacy

- The **website is public** (anyone can see the plan and code).
- Your **logs and history are not** — they stay in your browser and in any
  JSON/CSV files you export. `journal-export.json`, `history.csv`,
  `docs/training-history.md`, and `data/history-summary.json` are all
  git-ignored; never commit them or your Strava files to a public repo.

## Troubleshooting

- **Data not showing on a new device?** Export JSON on the old device, then
  Import it on the new one.
- **Progress looks empty?** It only counts dates you've logged — start with a few.
- **Need to fix a session?** Open that date in **Calendar**, edit the fields,
  and Save again.
