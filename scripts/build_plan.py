#!/usr/bin/env python3
"""Build data/plan.js for the 12-month run + kettlebell plan.

The plan is a **dated progression**, Oct 1 2026 -> Oct 3 2027, split into six
phases. Session content, run time, intensity, details, kettlebell work and
notes are read from the "Daily Schedule" sheet of Training Plan (1).xlsx, so the
website always matches the spreadsheet.

  * Dates come from the sheet's Date column. The sheet's `Day` column is known
    to be mislabeled (it runs one day ahead of the real weekday), so we IGNORE
    it and derive the weekday from the date. Trusting the dates reproduces the
    intended Sun -> Sat template:

      Sun  long run        (easy Z2)
      Mon  quality 1: threshold
      Tue  easy Z2 + KB B  (strides on some weeks)
      Wed  quality 2: VO2 / sprints / race-week sharpener
      Thu  easy Z2 + strides  (or KB C on rest days)
      Fri  rest / easy     (KB C on rest days)
      Sat  easy Z2 + strides

  * Out-of-range dates (before the plan starts or after it ends) fall back to a
    repeating Sun -> Sat A/B weekly template so the app can resolve *any* date.

Zones/paces still come from the workbook's "Zones & Sessions" sheet.
Run: python3 scripts/build_plan.py
"""

import datetime
import json
import os
import re

import openpyxl

WEEKDAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
XLSX = os.path.join(ROOT, "Training Plan (1).xlsx")
OUT_JS = os.path.join(ROOT, "data", "plan.js")
OUT_JSON = os.path.join(ROOT, "data", "plan.json")

# --- Fallback weekly template (only used outside the dated plan window) -------
KB_A = ("KB A – Hinge & Press (~35'): One-arm swings 4×10 each | "
        "Single-leg RDL (one KB) 3×8 each | Double-KB press 4×5 | "
        "Renegade row 3×5 each | Turkish get-up 3×2 each | Double farmer carry 4×40s")
KB_B = ("KB B – Upper & Core (~25'): Halos 3×8 each way | Double-KB press 4×5 | "
        "Double-KB bent-over row 4×8 | Turkish get-up 3×2 each | "
        "Windmill 2×5 each | Dead bug 3×8 each")
KB_C = ("KB C – Squat, Single-Leg & Carry (~35'): Double-KB front squat 4×8 | "
        "Rear-foot-elevated split squat (goblet) 3×6 each | "
        "Single-leg calf raise 3×12 each | Step-up (stair/low box, double KB) 3×8 each | "
        "Rack carry (one KB) 3×45s each | Side plank 3×35s each")

EASY = "Zone 2 – easy (RPE 3–4)"
THRESHOLD = "Threshold – Zone 4 (RPE 6–7)"
VO2 = "VO2 Max – Zone 5 (RPE 8–9)"
SPRINT = "Sprint / neuromuscular (RPE 8–9, full recovery)"

# Session kind -> zone code (drives the app's colour chips).
ZONE_BY_KIND = {
    "subthreshold": "Z3",
    "threshold": "Z4",
    "vo2": "Z5",
    "speed": "SPD",
    "easy": "Z2",
    "long": "Z2",
    "test": "TEST",
    "rest": "",
}

# Offsets documented in the "Zones & Sessions" sheet (seconds per mile vs. the
# 20-min TT pace). Only used to re-derive the pace text when the sheet's formula
# cache is empty — openpyxl drops cached values whenever the workbook is edited
# programmatically, so the "yellow edit me" cell B4 still works after a scripted
# edit. Edit the rule text in the sheet and mirror it here if you change them.
PACE_OFFSETS = [
    ("easy", 100, 150),
    ("sub-threshold", 25, 35),
    ("lactate threshold", 15, 20),
    ("vo2", -10, -5),
]


def clean(value):
    if value is None:
        return None
    text = str(value).strip()
    if text in {"", "—", "–", "-", "--", "n/a", "N/A"}:
        return None
    return text


def easy_run(minutes, strides=False):
    details = "Easy aerobic run %d' (Zone 2, talk-test pace)" % minutes
    if strides:
        details += " | finish with 5×15s strides (relaxed-fast, 45–60s walk/jog between)"
    return details


def build_week(variant):
    """Return the 7 fallback template entries (Sun..Sat) for week variant 'A'/'B'."""
    a_week = variant == "A"

    sun = {
        "session": "Rest from running + KB A",
        "kind": "rest", "zone": "", "runMin": 0, "intensity": "—",
        "details": "No running — kettlebell session only.",
        "kb": KB_A, "kbCode": "A",
        "notes": "Strength day. Stop each set ~2 reps shy of failure; quality running always wins.",
    }
    mon = {
        "session": "Quality 1: Threshold",
        "kind": "threshold", "zone": "Z4", "runMin": 40, "intensity": THRESHOLD,
        "details": "WU 10' easy jog + drills | 3×8' @ threshold (1' easy jog between) | CD 6' easy",
        "kb": None, "kbCode": None,
        "notes": "Run by effort. Once comfortable, progress by pace (3–5 sec/mi), not volume.",
    }
    tue = {
        "session": "Easy Zone 2 + KB B",
        "kind": "easy", "zone": "Z2", "runMin": 40, "intensity": EASY,
        "details": easy_run(40, strides=a_week),
        "kb": KB_B, "kbCode": "B",
        "notes": ("Strides prime you for tomorrow's quality work."
                  if a_week else
                  "Keep it genuinely easy. KB B can be done after the run, at lunch, or split into desk-break blocks."),
    }
    if a_week:
        wed = {
            "session": "Quality 2: VO2 Max",
            "kind": "vo2", "zone": "Z5", "runMin": 40, "intensity": VO2,
            "details": "WU 10' easy jog + drills | 5×3' @ VO2 effort (~3K–5K race effort) (2' easy jog between) | CD 7' easy",
            "kb": None, "kbCode": None,
            "notes": "Hard but repeatable — last rep ≈ first rep. Jog the recoveries, don't stop.",
        }
    else:
        wed = {
            "session": "Quality 2: Sprints/Strides",
            "kind": "speed", "zone": "SPD", "runMin": 38, "intensity": SPRINT,
            "details": "WU 15' easy jog + drills | 6×10s hill sprints (walk down, ≥90s recovery; flat accelerations if no hill) | CD 13' easy",
            "kb": None, "kbCode": None,
            "notes": "Quality over quantity: stop if form degrades. Full recovery between reps.",
        }
    thu = {
        "session": "No running + KB C",
        "kind": "rest", "zone": "", "runMin": 0, "intensity": "—",
        "details": "No running — kettlebell session only. Moderate legs — stop every set ~2 reps shy of failure.",
        "kb": KB_C, "kbCode": "C",
        "notes": "Keep legs moderate so Friday's strides and Saturday's long run stay fresh.",
    }
    fri = {
        "session": "Easy Zone 2 + strides",
        "kind": "easy", "zone": "Z2", "runMin": 35, "intensity": EASY + "; strides ~7",
        "details": easy_run(35, strides=True),
        "kb": None, "kbCode": None,
        "notes": "Shakeout before tomorrow's long run.",
    }
    sat = {
        "session": "Long Run",
        "kind": "long", "zone": "Z2", "runMin": 80, "intensity": "Zone 2 – easy (RPE 3–4)",
        "details": "Long run 80' easy (Zone 2). Steady and relaxed — finish feeling you could run 10–15' more.",
        "kb": None, "kbCode": None,
        "notes": "From ~60–75' on, practice fueling: water + roughly 30–60 g carbs/hr.",
    }

    entries = [sun, mon, tue, wed, thu, fri, sat]
    for i, e in enumerate(entries):
        e["dow"] = i
        e["weekday"] = WEEKDAYS[i]
        e["variant"] = variant
    return entries


def classify(session):
    """Map a sheet session name to an app 'kind'."""
    s = (session or "").lower()
    if s.startswith("race"):
        return "test"
    if "time trial" in s:
        return "test"
    # Norwegian singles: sub-threshold is *moderate*, so it gets its own kind and
    # must be tested before the plain "threshold" match below.
    if "sub-threshold" in s or "subthreshold" in s:
        return "subthreshold"
    if "threshold" in s:
        return "threshold"
    if "vo2" in s:
        return "vo2"
    if "hill" in s or "sprint" in s or "stride" in s:
        return "speed"
    if s.startswith("long"):
        return "long"
    if s.startswith("easy"):
        return "easy"
    if s.startswith("rest"):
        return "rest"
    return "easy"


def fmt_pace(seconds):
    seconds = int(round(seconds))
    return "%d:%02d" % (seconds // 60, seconds % 60)


def derive_pace(name, tt_secs):
    """Pace text for a zone, derived from the 20-min TT pace when the sheet's
    cached formula result is unavailable."""
    if tt_secs is None:
        return None
    key = (name or "").lower()
    for prefix, lo, hi in PACE_OFFSETS:
        if key.startswith(prefix):
            return "%s – %s" % (fmt_pace(tt_secs + lo), fmt_pace(tt_secs + hi))
    return None


def split_kb(text):
    """Return (exercise_list, kb_code) with the 'KB X – Title (...):' header removed."""
    if text is None:
        return None, None
    m = re.match(r"^KB\s+([ABC])\b", text)
    code = m.group(1) if m else None
    body = re.sub(r"^KB\s+[A-Z]\s*[–-]\s*[^:]*:\s*", "", text).strip()
    return (body or None), code


def js_dow(dt):
    return (dt.weekday() + 1) % 7  # JS getDay(): Sun=0 .. Sat=6


def as_int(value):
    if isinstance(value, float):
        return int(value)
    if isinstance(value, int):
        return value
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def parse_schedule(wb):
    """Read the Daily Schedule sheet into (schedule, weeks, phases)."""
    ws = wb["Daily Schedule"]
    rows = list(ws.iter_rows(values_only=True))

    header = next((i for i, r in enumerate(rows) if clean(r[0]) == "Week"), None)
    if header is None:
        raise RuntimeError("Daily Schedule: header row not found")

    schedule = {}
    week_agg = {}
    phases = []

    for row in rows[header + 1:]:
        dt = row[1]
        if not isinstance(dt, (datetime.datetime, datetime.date)):
            continue
        if isinstance(dt, datetime.datetime):
            dt = dt.date()
        session = clean(row[4])
        if not session:
            continue

        iso = dt.isoformat()
        kind = classify(session)
        kb_body, kb_code = split_kb(clean(row[8]))
        week = as_int(row[0])
        run_min = as_int(row[5])
        phase = clean(row[3])

        schedule[iso] = {
            "session": session,
            "kind": kind,
            "zone": ZONE_BY_KIND.get(kind, ""),
            "runMin": run_min,
            "intensity": clean(row[6]) or "—",
            "details": clean(row[7]) or "",
            "kb": kb_body,
            "kbCode": kb_code,
            "notes": clean(row[9]),
            "week": week,
            "phase": phase,
            "dow": js_dow(dt),
            "weekday": dt.strftime("%a"),
        }

        agg = week_agg.get(week)
        if agg is None:
            agg = week_agg[week] = {
                "week": week, "phase": phase,
                "start": iso, "end": iso,
                "longMin": 0, "totalRunMin": 0, "quality": 0,
            }
        agg["start"] = min(agg["start"], iso)
        agg["end"] = max(agg["end"], iso)
        agg["totalRunMin"] += run_min
        if kind == "long":
            agg["longMin"] = max(agg["longMin"], run_min)
        if kind in ("threshold", "vo2", "speed"):
            agg["quality"] += 1

        known = next((p for p in phases if p["name"] == phase), None)
        if known is None:
            phases.append({"name": phase, "start": iso, "end": iso})
        else:
            known["start"] = min(known["start"], iso)
            known["end"] = max(known["end"], iso)

    weeks = [week_agg[k] for k in sorted(week_agg)]
    return schedule, weeks, phases


def parse_zones(wb, tt_miles=None):
    try:
        tt_secs = 1200.0 / float(tt_miles) if tt_miles else None
    except (TypeError, ValueError):
        tt_secs = None

    ws = wb["Zones & Sessions"]
    rows = list(ws.iter_rows(values_only=True))
    zones = []
    started = False
    for row in rows:
        c0 = clean(row[0])
        if c0 and c0.lower().startswith("intensity system"):
            started = True
            continue
        if not started or not c0:
            continue
        if clean(row[2]) is None and clean(row[3]) is None:
            continue
        zones.append({
            "name": c0,
            "purpose": clean(row[1]),
            "rpe": clean(row[2]),
            "pace": clean(row[3]) or derive_pace(c0, tt_secs),
            "rule": clean(row[4]),
            "sessions": clean(row[5]),
            "frequency": clean(row[6]),
        })
    return zones


def parse_footer(wb):
    ws = wb["Zones & Sessions"]
    rows = list(ws.iter_rows(values_only=True))
    tt_miles = None
    rotation = []
    note = None
    for row in rows:
        c0 = clean(row[0])
        c1 = clean(row[1])
        if not c0:
            continue
        if c0.startswith("20-min time trial distance"):
            tt_miles = row[1]
        elif c0 in ("Week A (even weeks)", "Week B (odd weeks)",
                    "Down weeks (every 4th)", "Kettlebell placement"):
            rotation.append({"label": c0, "text": c1})
        elif c0.startswith("Paces are estimates"):
            note = c0
    return tt_miles, rotation, note


def main():
    wb = openpyxl.load_workbook(XLSX, data_only=True)
    tt_miles, _rotation, zones_note = parse_footer(wb)
    zones = parse_zones(wb, tt_miles)

    # The workbook's "frequency" text predates the current layout; keep it in
    # sync with the authoritative schedule (see AGENTS.md).
    freq_override = {
        "easy": "Most of the week (3–4 runs + long run)",
        "sub-threshold": "1–2×/week (Monday) in the base + sharpen blocks",
        "lactate threshold": "Most weeks (Monday)",
        "vo2": "Most weeks (Wednesday)",
        "short sprints": "Every other week (Wednesday) + weekly strides",
    }
    for z in zones:
        name = (z.get("name") or "").lower()
        for key, value in freq_override.items():
            if name.startswith(key):
                z["frequency"] = value
                break

    schedule, weeks, phases = parse_schedule(wb)
    start = min(schedule)
    end = max(schedule)

    plan = {
        "meta": {
            "title": "2027 Racing Season — Running + Kettlebell Plan",
            "goal": "Two races in 2027: St Paddy's 5 Miler (Mar 7 — sub-31:00 for Bloomsday "
                    "second seed) and the Bloomsday 12K (May 2). Lydiard conditioning plus "
                    "Norwegian singles, built around family and work.",
            "note": "A dated progression (Oct 2026 – Oct 2027): light reset → base build → hills "
                    "+ sharpen → 5-mile peak → Bloomsday 12K → general/half-marathon block. "
                    "Sub-threshold singles (RPE 5–6) are MODERATE, not hard. Dates outside the "
                    "plan fall back to a repeating A/B weekly template.",
            "timeTrialMiles": tt_miles,
            "zonesNote": zones_note,
            "anchor": start,
            "start": start,
            "end": end,
        },
        "template": {"A": build_week("A"), "B": build_week("B")},
        "schedule": schedule,
        "weeks": weeks,
        "phases": phases,
        "zones": zones,
    }

    with open(OUT_JSON, "w") as fh:
        json.dump(plan, fh, indent=2)
    with open(OUT_JS, "w") as fh:
        fh.write("// Generated by scripts/build_plan.py — do not edit by hand.\n")
        fh.write("window.PLAN = ")
        json.dump(plan, fh, separators=(",", ":"))
        fh.write(";\n")

    print("schedule: %d days, %d weeks, %d phases (%s -> %s); zones=%d"
          % (len(schedule), len(weeks), len(phases), start, end, len(zones)))


if __name__ == "__main__":
    main()
