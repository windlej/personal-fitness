# Norwegian singles — working reference

The method this plan is built on, distilled for coaching use. Primary source:
`docs/reference/norwegian-singles-guide.md` (the full upstream guide). This file
is the short version the coach should read first; the full guide is for detail,
citations and edge cases.

**Sub-threshold singles are MODERATE, not hard.** They do not count against the
two-hard-days-per-week budget. That is the whole point of the method and the
single most important thing to get right when coaching it.

## What it is

Frequent, *single* sub-threshold workouts — one per day, never doubled — spread
across the week and separated by genuinely easy running. It is the recreational
adaptation of the Norwegian double-threshold model, designed for roughly 5–9
hours of training per week. The goal is to raise the speed you can hold at a
*manageable* effort, repeatably, for months.

It is a **framework, not a calendar.** The published weeks are examples. Adapt
them to the athlete's real life and real current fitness.

## The week

The guide's example week and this athlete's version differ in one deliberate
way: the long easy run is **Saturday** and the longest sub-threshold is
**Monday**. That protects the anchor session — Sunday is off running, so Monday
is the freshest day of the week — and matches the long run to the habit already
in the plan.

| Day | Session | Kind |
|-----|---------|------|
| Sun | Rest from running + KB A | rest |
| **Mon** | **Quality 1 — longest sub-threshold** | subthreshold |
| Tue | Easy + KB B | easy |
| Wed | Quality 2 — medium sub-threshold | subthreshold |
| Thu | Rest + KB C | rest |
| Fri | Easy, or Quality 3 — shortest sub-threshold | easy / subthreshold |
| **Sat** | **Long run, easy** | long |

Notes on the shape:

- The third (Friday) session only appears once two sessions and the current
  mileage are comfortably absorbed. When it does, Friday must stay the
  **shortest** session of the week, because Saturday's long run follows it.
- A race or time trial replaces a quality session. It is never added on top.
- Sunday is protected. Running seven days makes Monday — the session the whole
  week is built around — the least-fresh day.

## The sessions

Duration-based, from the guide. Use current race fitness, start at the slower
end, and adjust for heat, hills and wind before starting.

| Repetition | Starting pace guide | Recovery |
|---|---|---|
| ~3 minutes | 12–15K race pace | 60 s |
| ~6 minutes | ~20K / half-marathon pace | 60–90 s |
| ~10 minutes | 25–30K race pace | 90–120 s |

A complete session is ~10' easy warm-up, the repetitions, then 7–10' easy
cool-down. Eight 3' reps with seven 1' recoveries therefore costs ~48–51'
total. Shorten the rep count to fit current training — the examples are not
minimums.

**How much work:** quality reps should total roughly 20–25% of weekly running
time once the athlete is established. Count only the repetitions. Three sessions
of 24' = 72 quality minutes, not three hours.

## Intensity control

Judge a session by whether the athlete recovers for the next one. Use all of
these together, and let effort win when they disagree:

- **Pace** — from *current* fitness, not a personal best and not a goal time.
  Stale anchors are the most common failure mode in this method.
- **Heart rate** — individual LTHR is the guardrail. A field estimate is the
  average HR over the final 20' of a well-paced solo 30' maximum effort. Early
  reps typically finish 10–15 bpm below LTHR, with later reps approaching it
  from below. Repeatedly exceeding LTHR means the pace is too fast.
- **Perceived effort** — breathing controlled, work manageable, enough left for
  another rep. Finish the planned session rather than testing that reserve.
- **Easy running** — a ceiling of ~70% of measured max HR, and often lower.
  This is a ceiling, not a target.

For this athlete: max HR ≈ 190, so the easy ceiling is **~133 bpm** and LTHR is
**~172** (estimated). Recent evidence (3×6' at 6:57–7:06, HR 162–166) is
consistent with both.

## Progression

1. **Start from recent training.** Keep total weekly running time near what is
   already sustained. Replace existing hard sessions rather than adding on top.
2. **Consolidate before increasing.** A month at a manageable level, then a
   small increase held for two or three weeks.
3. **Add time gradually, one small change at a time.** Adding one 3' rep across
   the week pairs with roughly 12 extra easy minutes.
4. **Earn pace through fitness.** Reassess with a race or time trial every 4–8
   weeks, not because a calendar block ended.
5. **Hold or reduce** when recovery deteriorates, even if the plan says build.

Day count follows the same rule: **add a running day after two consecutive
weeks at target with quiet shins and easy runs that still feel easy.** Not on a
schedule.

## Long run

An extension of easy running, not a second workout. The guide suggests roughly
1.7× an ordinary easy run (45' easy → ~75–80'), with higher-volume examples at
95–105'. Scale from the athlete's established longest run. Keep it easy.

## Racing, time trials, missed runs

- **Race replaces a quality slot.** No dedicated taper for an ordinary 5K; keep
  the surrounding week familiar. A priority race justifies more freshening.
- **After a race:** easy running first, then make the first quality session
  gentler. Do not make up the omitted quality work.
- **Missed run:** resume the schedule. Never cram it into the following easy
  day.
- **Tired day:** drop to the slower (10'-rep) pace, cut a rep, or make it an
  easy run. Persistent fatigue means reduce load, not push through.

## Terms

- **LT1 / LT2** — the first and second lactate thresholds. Easy running sits
  below LT1; sub-threshold work sits below LT2.
- **Sub-threshold** — controlled work just under LT2. "Moderate": harder than
  easy, far short of a race effort.
- **Single** — one standalone quality session in a day, as opposed to the
  elite double-threshold model (two sessions, morning and afternoon).
- **RPE** — rating of perceived exertion, 1–10.
- **LTHR** — lactate-threshold heart rate; the HR guardrail for quality work.
- **TSS / CTL / ATL / TSB** — training-stress score, chronic and acute load, and
  training-stress balance ("fitness", "fatigue", "form"). Useful trends, never a
  substitute for how the athlete actually feels.
- **Critical power / critical speed** — model-based estimates. Not the same
  thing as LT2; do not treat one as the other.

## What this framework does not include

No default VO2max block, no doubles, no marathon adaptation, and no assumption
that speed work is needed. Strides, hills and strength are optional additions —
the kettlebell work in this plan is kept because it protects running, and its
fatigue is accounted for when planning running.

## Where the block lives

The Nov 2026 – Jan 2027 singles ramp is generated in `scripts/build_plan.py`
(`SINGLES_WEEKS` / `build_singles_block`), not in the workbook. Its sessions are
marked `effortOnly`, so the app shows the HR guardrail but withholds a pace
target until the 2027-01-17 time trial resets the pace model.
