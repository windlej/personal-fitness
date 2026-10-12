---
name: modify-training-plan
description: Use when changing the weekly training template, adjusting run durations or kettlebell blocks, updating zones/paces, adding or editing a race goal, or rebuilding data/plan.json. Triggers on "change the plan", "adjust my training", "add a race", "make Tuesday easier", "long run longer", "rebuild plan".
---

# Modify the training plan

The training plan is a **generated artifact**. Edit the source, rebuild, verify,
then commit. Never hand-edit `data/plan.js` or `data/plan.json` — they are
overwritten on every build.

## Source of truth

| Want to change | Edit |
|----------------|------|
| Sessions, run durations, intervals, KB blocks | `scripts/build_plan.py` → `build_week()` |
| Zones, paces, zone purposes | `Training Plan (1).xlsx` → "Zones & Sessions" sheet |
| Goal / framing text | `scripts/build_plan.py` → `main()` → `meta` |
| Athlete goals, constraints, injuries | `docs/training-context.md` |
| App behavior / display | `js/app.js` |

## Workflow

1. **Clarify the goal.** Restate the change and its training intent (e.g. "make
   the midweek quality session shorter during a busy month"). If it conflicts
   with `docs/training-context.md` constraints, say so.
2. **Edit `scripts/build_plan.py`.** Keep the Sun → Sat order and the A/B
   structure. Helper constants (`EASY`, `THRESHOLD`, `VO2`, `SPRINT`, `KB_A`,
   `KB_B`, `KB_C`, `easy_run()`) are defined near the top — reuse them.
3. **Rebuild:**
   ```bash
   python3 scripts/build_plan.py
   ```
   Expect: `template weeks: A/B, 7 days each; zones=<n>`.
4. **Verify.** Syntax-check the generated app data and preview the affected view:
   ```bash
   node --check data/plan.js
   python3 -m http.server 8000   # open http://localhost:8000
   ```
5. **Show the diff** (`git diff data/plan.json`) and confirm before committing.
6. Commit on `main` and push; GitHub Pages redeploys automatically.

## Guardrails

- Keep quality days on **Mon** and **Wed**; never put two hard days back-to-back.
- Weekday runs ≤ 40', long run ≤ 90' unless the athlete is specifically building
  to more and asks.
- Progress one variable at a time (reps/time first, then pace).
- KB sessions stay moderate; stop ~2 reps shy of failure.
- If `openpyxl` is missing: `python3 -m pip install openpyxl`.

## Adding a race / goal

The plan is undated, so a race becomes a **focus block**, not a calendar:

1. Record the race in `docs/training-context.md` (distance, date, goal time).
2. Translate it into template tweaks, e.g.:
   - **5K/10K:** keep VO2 on Wed; add a few 200–400 m reps to the threshold day.
   - **Half:** extend the long run gradually (add ~5–10' every 2–3 weeks, with a
     down week every 4th) and lengthen threshold intervals (e.g. 2×12', 20' tempo).
3. Add a taper: last 1–2 weeks cut volume ~30–40%, keep intensity short and sharp.
4. Rebuild, verify, and confirm the block with the athlete before committing.

## Examples

- _"Long run to 90'"_ → in `sat`, change `runMin` to 90 and the `details` text;
  rebuild.
- _"Swap Wednesday VO2 for a tempo"_ → edit the `a_week` `wed` dict.
- _"Fewer kettlebell days"_ → remove the `kb`/`kbCode` from a day and update
  `AGENTS.md` + `docs/training-context.md` to match the new intent.

After any plan change, keep `AGENTS.md`'s template table in sync with the build.
