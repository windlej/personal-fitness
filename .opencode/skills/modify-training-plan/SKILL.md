---
name: modify-training-plan
description: Use when changing the dated training schedule, adjusting run durations or kettlebell blocks, updating zones/paces, adding or editing a race goal, or rebuilding data/plan.json. Triggers on "change the plan", "adjust my training", "add a race", "make Tuesday easier", "long run longer", "rebuild plan".
---

# Modify the training plan

The training plan is a **generated artifact**. Edit the source, rebuild, verify,
then commit. Never hand-edit `data/plan.js` or `data/plan.json` — they are
overwritten on every build.

## Source of truth

The dated 12-month plan (Oct 2026 → Oct 2027) lives in the workbook's
**Daily Schedule** sheet and is parsed into `PLAN.schedule` by
`scripts/build_plan.py`. `build_week()` is only the out-of-range A/B fallback.

| Want to change | Edit |
|----------------|------|
| Sessions, run durations, intervals, KB blocks (dated) | `Training Plan (1).xlsx` → "Daily Schedule" sheet |
| Sessions outside the plan window (fallback) | `scripts/build_plan.py` → `build_week()` |
| Zones, paces, zone purposes | `Training Plan (1).xlsx` → "Zones & Sessions" sheet |
| Goal / framing text | `scripts/build_plan.py` → `main()` → `meta` |
| Athlete goals, constraints, injuries | `docs/training-context.md` |
| App behavior / display | `js/app.js` |

> **Sheet gotcha:** the Daily Schedule's `Day` column is mislabeled — it runs one
> day ahead of the real weekday. Trust the **Date** column; `build_plan.py`
> derives the weekday from it.

## Workflow

1. **Clarify the goal.** Restate the change and its training intent (e.g. "make
   the midweek quality session shorter during a busy month"). If it conflicts
   with `docs/training-context.md` constraints, say so.
2. **Edit the source.** For dated sessions, edit the **Daily Schedule** sheet and
   save the `.xlsx`. For the out-of-range fallback, edit `build_week()` in
   `scripts/build_plan.py`; reuse the helper constants (`EASY`, `THRESHOLD`,
   `VO2`, `SPRINT`, `KB_A`, `KB_B`, `KB_C`, `easy_run()`).
3. **Rebuild:**
   ```bash
   python3 scripts/build_plan.py
   ```
   Expect: `schedule: <N> days, <N> weeks, 6 phases (… -> …); zones=<n>`.
4. **Verify.** Syntax-check the generated app data and preview the affected view:
   ```bash
   node --check data/plan.js
   python3 -m http.server 8000   # open http://localhost:8000
   ```
5. **Show the diff** (`git diff data/plan.json`) and confirm before committing.
6. Commit on `main` and push; GitHub Pages redeploys automatically.

## Guardrails

- Keep quality days on the intended weekdays (Mon threshold, Wed quality 2);
  never put two hard days back-to-back.
- Weekday runs ≤ 40', long run ≤ 90' unless the athlete is specifically building
  to more and asks.
- Progress one variable at a time (reps/time first, then pace).
- KB sessions stay moderate; stop ~2 reps shy of failure.
- If `openpyxl` is missing: `python3 -m pip install openpyxl`.

## Adding a race / goal

The plan is dated, so a race is a **real calendar row** in the Daily Schedule:

1. Record the race in `docs/training-context.md` (distance, date, goal time).
2. Add the race date and a short taper to the Daily Schedule sheet (last 1–2
   weeks cut run volume ~30–40% while keeping intensity short and sharp). Label
   the race row `Race` so `build_plan.py` classifies it as `test`.
3. Rebuild, verify, and confirm the block with the athlete before committing.

## Examples

- _"Long run on 2026-11-07 to 90'"_ → edit that date's row in the Daily Schedule
  sheet (Run Min + Run Details); rebuild.
- _"Cap the whole plan's long runs at 90'" → edit the sheet rows, or (fallback
  only) the `sat` dict in `build_week()`.
- _"Fewer kettlebell days"_ → remove the KB from the relevant dated rows and
  update `AGENTS.md` + `docs/training-context.md`.

After any plan change, keep `AGENTS.md`'s template table in sync with the build.
