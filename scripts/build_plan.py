#!/usr/bin/env python3
"""Build data/plan.js for the continuous run + kettlebell plan.

The plan is a *continuous weekly template* rather than a fixed calendar. There
are two alternating weeks (A and B) that repeat forever, so you can open the app
on any date. Weeks run Sunday -> Saturday:

  Sun  rest from running + KB A (hinge & press)
  Mon  quality 1: threshold
  Tue  easy Z2 (+ strides on A weeks) + KB B (upper & core)
  Wed  quality 2: VO2 (A weeks) or sprints/strides (B weeks) — no kettlebell
  Thu  no running + KB C (squat / single-leg / carry)
  Fri  easy Z2 + strides
  Sat  long run, easy

Zones/paces are still read from the workbook so they stay in sync with the
"Zones & Sessions" sheet. Run:  python3 scripts/build_plan.py
"""

import datetime
import json
import os

import openpyxl

WEEKDAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
XLSX = os.path.join(ROOT, "Training Plan (1).xlsx")
OUT_JS = os.path.join(ROOT, "data", "plan.js")
OUT_JSON = os.path.join(ROOT, "data", "plan.json")

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
    """Return the 7 template entries (Sun..Sat) for week variant 'A' or 'B'."""
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


def parse_zones(wb):
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
            "pace": clean(row[3]),
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
    zones = parse_zones(wb)
    tt_miles, _rotation, zones_note = parse_footer(wb)

    plan = {
        "meta": {
            "title": "Continuous Running + Kettlebell Plan",
            "goal": "General fitness and fun — stay ready to run anything from 5K to "
                    "the half marathon. Train by effort; let RPE win over the watch.",
            "note": "A repeating Sun–Sat weekly template. Weeks alternate A and B. "
                    "Log how each session felt and adjust as life demands.",
            "timeTrialMiles": tt_miles,
            "zonesNote": zones_note,
            "anchor": "2026-10-04",
        },
        "template": {"A": build_week("A"), "B": build_week("B")},
        "zones": zones,
    }

    with open(OUT_JSON, "w") as fh:
        json.dump(plan, fh, indent=2)
    with open(OUT_JS, "w") as fh:
        fh.write("// Generated by scripts/build_plan.py — do not edit by hand.\n")
        fh.write("window.PLAN = ")
        json.dump(plan, fh, separators=(",", ":"))
        fh.write(";\n")

    print("template weeks: A/B, 7 days each; zones=%d" % len(zones))


if __name__ == "__main__":
    main()
