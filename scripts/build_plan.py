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

  * ONE EXCEPTION: the Norwegian singles ramp (2026-11-23 -> 2027-01-17) is
    generated here instead of read from the sheet, and its phase boundary is
    defined in PHASES below rather than in the sheet's Phase column. It is a
    progressive ramp that is easier to reason about as code, so the sheet is no
    longer the source of truth for those dates. See AGENTS.md.

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


# --- Norwegian singles ramp, 2026-11-23 -> 2027-01-17 ------------------------
# Generated here rather than in the workbook: it is a progressive ramp whose
# shape is easier to reason about (and adjust) as code. It replaces the sheet's
# session content for those dates only, and it inverts the guide's example
# calendar to protect the athlete's preferred week:
#
#   Sun  rest + KB A
#   Mon  LONGEST sub-threshold   (freshest day: Sunday is off running)
#   Tue  easy + KB B             (rest + KB B in the four-run weeks)
#   Wed  medium sub-threshold
#   Thu  rest + KB C             (a short shuffle in the six-day week)
#   Fri  easy, or the week's shortest sub-threshold
#   Sat  long run, easy          (HR <= 133 is a ceiling)
#
# Sub-threshold is MODERATE, so this block uses NONE of the two-hard-days budget:
# it contains no threshold or VO2 sessions at all. Paces are deliberately absent
# for weeks 1-5 (effort only); they are set from the 2027-01-17 time trial.

SINGLES_START = "2026-11-23"
SINGLES_END = "2027-01-17"

PHASES = [
    ("1 Re-Entry / Reset", "2026-09-30", "2026-11-22"),
    ("2 Base Build — Singles Ramp", "2026-11-23", "2027-01-17"),
    ("3 Hills + Sharpen", "2027-01-18", "2027-02-07"),
    ("4 5-Mile Peak", "2027-02-08", "2027-03-07"),
    ("5 Bloomsday 12K", "2027-03-08", "2027-05-02"),
    ("6 General / Half-Marathon", "2027-05-03", "2027-10-02"),
]

EASY_HR = "Zone 2 – easy (RPE 3–4; HR ≤133)"
SUB_HR = "Sub-threshold – RPE 5–6; HR ≤165 (moderate, not hard)"

# start (Mon), Mon quality, Tue easy, Wed, Thu, Fri, Sat long, is down week.
# Tue/Thu = 0 means a KB-only rest day. Wed/Fri = an int means an easy run, a
# (reps, rep-minutes) tuple means a sub-threshold session.
SINGLES_WEEKS = [
    ("2026-11-23", (3, 4), 0, 30, 0, 20, 40, False),
    ("2026-11-30", (3, 5), 0, 30, 0, 20, 42, False),
    ("2026-12-07", (3, 5), 20, (4, 3), 0, 16, 40, False),
    ("2026-12-14", (3, 4), 0, 29, 0, 16, 32, True),
    ("2026-12-21", (3, 5), 24, (4, 3), 0, 20, 44, False),
    ("2026-12-28", (2, 8), 24, (4, 3), 0, (3, 3), 46, False),
    ("2027-01-04", (2, 10), 16, (5, 3), 15, (3, 3), 42, False),
    ("2027-01-11", (2, 8), 20, 28, 0, 18, 28, False),
]

SUB_SLOTS = {
    # slot: (warm-up min, cool-down min, session name, notes)
    "long": (10, 9, "Quality 1: Sub-Threshold (long)",
             "Longest sub-threshold of the week — you are freshest here. "
             "Effort only: no pace target until the Jan 17 time trial."),
    "medium": (8, 8, "Quality 2: Sub-Threshold (medium)",
               "Medium session: short reps, controlled. The last rep should feel "
               "like the first — if it doesn't, you went too fast."),
    "short": (8, 6, "Quality 3: Sub-Threshold (short)",
              "Shortest session of the week. Stop at the planned reps even if you "
              "feel good — the recovery is the point."),
}


def sub_session(reps, rep_min, slot, cool_down=None, notes=None):
    wu, cd, name, slot_notes = SUB_SLOTS[slot]
    cd = cd if cool_down is None else cool_down
    rec = 2 if rep_min >= 10 else 1
    run_min = wu + reps * rep_min + (reps - 1) * rec + cd
    return {
        "session": name,
        "kind": "subthreshold",
        "zone": "Z3",
        "runMin": run_min,
        "intensity": SUB_HR,
        "details": ("WU %d' easy jog + drills | %d×%d' @ sub-threshold — effort only, "
                    "no pace target (RPE 5–6, HR ≤165; %d' easy jog between) | CD %d' easy"
                    % (wu, reps, rep_min, rec, cd)),
        "kb": None, "kbCode": None,
        "effortOnly": True,
        "notes": notes or slot_notes,
    }


def rest_session(kb_code, kb_text, details=None):
    return {
        "session": "Rest (KB only)" if kb_text else "Rest",
        "kind": "rest", "zone": "", "runMin": 0, "intensity": "—",
        "details": details or ("No running — kettlebell session only." if kb_text else "No running."),
        "kb": kb_text, "kbCode": kb_code,
        "notes": None,
    }


def easy_session(minutes, strides=False, kb=None, kb_code=None, notes=None):
    details = ("Easy aerobic run %d' (Zone 2, talk-test pace; HR ≤133 — a ceiling, "
               "not a target)" % minutes)
    if strides:
        details += (" | finish with 4×15s strides (relaxed-fast, 45–60s walk/jog between)")
    return {
        "session": "Easy Run", "kind": "easy", "zone": "Z2", "runMin": minutes,
        "intensity": EASY_HR, "details": details,
        "kb": kb, "kbCode": kb_code, "notes": notes,
    }


def long_session(minutes, notes=None):
    return {
        "session": "Long Run", "kind": "long", "zone": "Z2", "runMin": minutes,
        "intensity": EASY_HR,
        "details": ("Long run %d' easy (Zone 2; HR ≤133). Steady and relaxed — finish "
                    "feeling you could run 10–15' more." % minutes),
        "kb": None, "kbCode": None,
        "notes": notes or ("Easy means easy. Walk the hills; HR ≤133 is a ceiling, "
                           "not a target."),
    }


def build_singles_block():
    """Return {iso: entry} for every day of the singles ramp, closed by the 5K TT."""
    block = {}
    for start, mon, tue, wed, thu, fri, sat, down in SINGLES_WEEKS:
        monday = datetime.date.fromisoformat(start)
        for offset in range(7):
            day = monday + datetime.timedelta(days=offset)
            iso = day.isoformat()
            dow = js_dow(day)

            if dow == 0:                      # Sun — rest from running
                entry = rest_session("A", KB_A)
            elif dow == 1:                    # Mon — longest sub-threshold
                notes = None
                if down:
                    notes = ("Down week: ~30% less volume than last week. Keep it honest."
                             "\nLongest sub-threshold of the week — you are freshest here.")
                elif start == "2026-12-21":
                    notes = ("Benchmark: repeat week 1's session and compare your heart "
                             "rate at the same effort. Lower HR = fitter.")
                elif start >= "2026-12-28":
                    notes = ("Longest session of the week. Set the pace from the Dec 21 "
                             "benchmark; slower is always fine.")
                entry = sub_session(mon[0], mon[1], "long",
                                    cool_down=6 if down else None, notes=notes)
            elif dow == 2:                    # Tue — easy, or KB-only rest
                if tue:
                    entry = easy_session(
                        tue, kb=KB_B, kb_code="B",
                        notes=("KB B after the run, at lunch, or split into desk-break "
                               "blocks. Keep the run genuinely easy after Monday."))
                else:
                    entry = rest_session("B", KB_B)
            elif dow == 3:                    # Wed — medium quality, or easy
                if isinstance(wed, tuple):
                    entry = sub_session(wed[0], wed[1], "medium",
                                        cool_down=6 if down else None)
                else:
                    entry = easy_session(
                        wed, notes="Easy and flat. Nothing fast by accident.")
            elif dow == 4:                    # Thu — rest, or the 6th-day shuffle
                if thu:
                    entry = easy_session(
                        thu, kb=KB_C, kb_code="C",
                        notes=("First six-day week: a 15' shuffle only. Trim KB C to two "
                               "sets, not three."))
                else:
                    entry = rest_session("C", KB_C)
            elif dow == 5:                    # Fri — easy, or shortest quality
                if isinstance(fri, tuple):
                    entry = sub_session(fri[0], fri[1], "short")
                else:
                    entry = easy_session(
                        fri, strides=True,
                        notes="Shakeout before tomorrow's long run.")
            else:                             # Sat — the long easy run
                entry = long_session(sat)

            entry["dow"] = dow
            entry["weekday"] = day.strftime("%a")
            block[iso] = entry

    # The block closes on the 5K time trial — the fitness gate for the sub-31:00
    # 5-mile build. It replaces the long run that week.
    block["2027-01-17"] = {
        "session": "5K Time Trial",
        "kind": "test", "zone": "TEST", "runMin": 45,
        "intensity": "Time trial – flat out (RPE 9)",
        "details": ("WU 20' easy + drills + 4×20s strides | 3.1 mi time trial, flat out | "
                    "CD 15' easy. Use a flat, measured route or the track."),
        "kb": None, "kbCode": None,
        "notes": ("This is the gate and the pace-setter: it resets every pace target for "
                  "the St Paddy's build. Start controlled, finish empty."),
    }
    return block


# Two on-ramp weeks before the block. As of Nov 2026 the athlete is at ~2-3
# runs and ~100 min/week, so the ramp starts there — not at the sheet's
# optimistic 150 — and adds exactly one run per week before any quality appears.
RAMP_WEEKS = [
    # start (Mon), Mon, Tue, Wed, Thu, Fri, Sat long   (0 = rest day for that slot)
    ("2026-11-09", 32, 0, 30, 0, 0, 38),
    ("2026-11-16", 30, 0, 30, 0, 18, 42),
]


def build_ramp_block():
    """Easy-only on-ramp weeks: no quality, one added run per week."""
    block = {}
    for start, mon, tue, wed, thu, fri, sat in RAMP_WEEKS:
        for offset in range(7):
            day = datetime.date.fromisoformat(start) + datetime.timedelta(days=offset)
            iso, dow = day.isoformat(), js_dow(day)
            if dow == 0:
                entry = rest_session("A", KB_A)
            elif dow == 1:
                entry = easy_session(mon, notes="On-ramp week: easy only, no quality yet.")
            elif dow == 2:
                entry = easy_session(tue, kb=KB_B, kb_code="B") if tue else rest_session("B", KB_B)
            elif dow == 3:
                entry = easy_session(wed, notes="Easy and flat. Nothing fast by accident.")
            elif dow == 4:
                entry = easy_session(thu, kb=KB_C, kb_code="C") if thu else rest_session("C", KB_C)
            elif dow == 5:
                entry = easy_session(fri, strides=True, notes="Shakeout before tomorrow's long run.") if fri else rest_session(None, None)
            else:
                entry = long_session(sat)
            entry["dow"], entry["weekday"] = dow, day.strftime("%a")
            block[iso] = entry
    return block


def phase_for(iso):
    for name, start, end in PHASES:
        if start <= iso <= end:
            return name
    return None


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

    return schedule


def aggregate(schedule):
    """Recompute per-week totals and the phase list from a finished schedule."""
    weeks = {}
    for iso in sorted(schedule):
        e = schedule[iso]
        phase = phase_for(iso)
        if phase:
            e["phase"] = phase

        agg = weeks.get(e["week"])
        if agg is None:
            agg = weeks[e["week"]] = {
                "week": e["week"], "phase": e.get("phase"),
                "start": iso, "end": iso,
                "longMin": 0, "totalRunMin": 0, "quality": 0, "moderate": 0,
                "_phase_counts": {},
            }
        agg["start"] = min(agg["start"], iso)
        agg["end"] = max(agg["end"], iso)
        if e.get("phase"):
            agg["_phase_counts"][e["phase"]] = agg["_phase_counts"].get(e["phase"], 0) + 1
        agg["totalRunMin"] += e.get("runMin") or 0
        if e.get("kind") == "long":
            agg["longMin"] = max(agg["longMin"], e.get("runMin") or 0)
        if e.get("kind") in ("threshold", "vo2", "speed"):
            agg["quality"] += 1
        if e.get("kind") == "subthreshold":
            agg["moderate"] += 1

    ordered = [weeks[k] for k in sorted(weeks)]
    # The app's week grid is Sun -> Sat while the singles block runs Mon -> Sun,
    # so the first block week and the week closing on the time trial straddle a
    # phase boundary. Label each week by the phase most of its days belong to.
    for w in ordered:
        counts = w.pop("_phase_counts", {})
        if counts:
            w["phase"] = max(counts, key=counts.get)
    phases = [{"name": n, "start": s, "end": e} for n, s, e in PHASES]
    return ordered, phases


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
        "easy": "3–4 runs/week + the long run",
        "sub-threshold": "2–3×/week (Mon long, Wed medium, Fri short) in the singles block",
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

    schedule = parse_schedule(wb)

    # Replace the sheet's content for the singles ramp. Week numbers come from
    # the sheet so the app's week grid (Sun -> Sat) keeps its numbering; every
    # block Sunday is a zero-minute rest day, so each app week still totals
    # exactly one Mon -> Sat block week.
    block = build_singles_block()
    ramp = build_ramp_block()
    for iso, entry in list(ramp.items()) + list(block.items()):
        if iso not in schedule:
            raise RuntimeError("overlay adds a date outside the schedule: %s" % iso)
        entry["week"] = schedule[iso]["week"]
        schedule[iso] = entry

    weeks, phases = aggregate(schedule)
    start = min(schedule)
    end = max(schedule)

    plan = {
        "meta": {
            "title": "2027 Racing Season — Running + Kettlebell Plan",
            "goal": "Two races in 2027: St Paddy's 5 Miler (Mar 7 — sub-31:00 for Bloomsday "
                    "second seed) and the Bloomsday 12K (May 2). Lydiard conditioning plus "
                    "Norwegian singles, built around family and work.",
            "note": "A dated progression (Oct 2026 – Oct 2027): light reset → singles ramp → "
                    "hills + sharpen → 5-mile peak → Bloomsday 12K → general/half-marathon "
                    "block. The singles ramp (Nov 23 – Jan 17) builds from ~100 to ~180 "
                    "min/week across two or three sub-threshold sessions; it contains no hard "
                    "days. Sub-threshold singles (RPE 5–6) are MODERATE, not hard. Dates "
                    "outside the plan fall back to a repeating A/B weekly template.",
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
