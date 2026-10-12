#!/usr/bin/env python3
"""Build data/plan.js from the training plan workbook.

The Daily Schedule sheet in the source workbook stores dates one day earlier
than the weekday labels it prints (a generation bug). Phase 1 is documented as
starting Thursday Oct 1 2026 and the first quality session as Tue Oct 6 2026, so
we trust the weekday labels and shift daily dates forward one day. Weekly
Summary dates are already correct and are left untouched.

Run:  python3 scripts/build_plan.py
"""

import datetime
import json
import os
import re

import openpyxl

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
XLSX = os.path.join(ROOT, "Training Plan (1).xlsx")
OUT_JS = os.path.join(ROOT, "data", "plan.js")
OUT_JSON = os.path.join(ROOT, "data", "plan.json")


def clean(value):
    if value is None:
        return None
    text = str(value).strip()
    if text in {"", "—", "–", "-", "--", "n/a", "N/A"}:
        return None
    return text


def to_date(value):
    if isinstance(value, datetime.datetime):
        return value.date()
    if isinstance(value, datetime.date):
        return value
    return None


def classify(session, notes):
    s = (session or "").lower()
    n = (notes or "").lower()
    if "time trial" in s or "race" in s:
        kind = "test"
    elif "long run" in s:
        kind = "long"
    elif "vo2" in s:
        kind = "vo2"
    elif "sprint" in s or "stride" in s:
        kind = "speed"
    elif "threshold" in s:
        kind = "threshold"
    elif "easy" in s:
        kind = "easy"
    elif "rest" in s:
        kind = "rest"
    else:
        kind = "other"
    optional = "optional" in s or "optional" in n
    down = "down week" in n
    return kind, optional, down


def zone_code(intensity):
    i = (intensity or "").lower()
    if "zone 2" in i:
        return "Z2"
    if "zone 4" in i or "threshold" in i:
        return "Z4"
    if "zone 5" in i or "vo2" in i:
        return "Z5"
    if "sprint" in i or "neuromuscular" in i:
        return "SPD"
    if "hard steady" in i:
        return "TEST"
    return ""


def kb_code(kb):
    if not kb:
        return None
    m = re.match(r"KB\s*([ABC])\b", kb.strip(), re.IGNORECASE)
    return m.group(1).upper() if m else None


def first_line(text, fallback=None):
    if not text:
        return fallback
    return text.split("|")[0].strip() or fallback


def parse_days(wb):
    ws = wb["Daily Schedule"]
    rows = list(ws.iter_rows(values_only=True))
    days = []
    for row in rows:
        if not row or row[0] == "Week" or row[1] is None:
            continue
        date = to_date(row[1])
        if date is None:
            continue
        date = date + datetime.timedelta(days=1)  # correct the off-by-one
        session = clean(row[4])
        details = clean(row[7])
        kb = clean(row[8])
        notes = clean(row[9])
        kind, optional, down = classify(session, notes)
        days.append({
            "week": int(row[0]),
            "date": date.isoformat(),
            "weekday": clean(row[2]),
            "phase": clean(row[3]),
            "phaseNum": int(str(row[3]).split()[0]) if row[3] else None,
            "session": session,
            "kind": kind,
            "optional": optional,
            "down": down,
            "runMin": int(row[5]) if row[5] not in (None, "") else 0,
            "intensity": clean(row[6]),
            "zone": zone_code(row[6]),
            "details": details,
            "detailsTitle": first_line(details),
            "kb": kb,
            "kbCode": kb_code(kb),
            "kbTitle": first_line(kb),
            "notes": notes,
        })
    days.sort(key=lambda d: d["date"])
    return days


def parse_weeks(wb):
    ws = wb["Weekly Summary"]
    rows = list(ws.iter_rows(values_only=True))
    weeks = []
    for row in rows:
        if not row or not isinstance(row[0], (int, float)) or row[1] is None:
            continue
        start = to_date(row[1])
        end = to_date(row[2])
        if start is None:
            continue
        weeks.append({
            "week": int(row[0]),
            "start": start.isoformat(),
            "end": end.isoformat() if end else None,
            "phase": clean(row[3]),
            "type": clean(row[4]),
            "qualityMix": clean(row[5]),
            "runDays": int(row[6]) if isinstance(row[6], (int, float)) else None,
            "totalRunMin": int(row[7]) if isinstance(row[7], (int, float)) else None,
            "longRunMin": int(row[8]) if isinstance(row[8], (int, float)) else None,
            "kbSessions": int(row[10]) if isinstance(row[10], (int, float)) else None,
            "focus": clean(row[11]),
        })
    weeks.sort(key=lambda w: w["week"])
    return weeks


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


def parse_kb(wb):
    ws = wb["Kettlebell Plan"]
    rows = list(ws.iter_rows(values_only=True))
    levels = []
    for row in rows:
        c0 = clean(row[0])
        if not c0 or not re.match(r"^\d+\.", c0):
            continue
        levels.append({
            "level": c0,
            "weeks": clean(row[1]),
            "a": clean(row[2]),
            "b": clean(row[3]),
            "c": clean(row[4]),
        })
    return levels


def parse_meta(wb):
    ws = wb["Read Me"]
    rows = [clean(r[0]) for r in ws.iter_rows(values_only=True) if r[0]]
    # The Read Me tab is a flat list of paragraphs.
    return rows


def main():
    wb = openpyxl.load_workbook(XLSX, data_only=True)
    days = parse_days(wb)
    weeks = parse_weeks(wb)
    zones = parse_zones(wb)
    kb = parse_kb(wb)
    meta_rows = parse_meta(wb)
    tt_miles, rotation, zones_note = parse_footer(wb)

    plan = {
        "meta": {
            "title": "12-Month Running + Kettlebell Plan",
            "goal": "General fitness and fun — run anything from 5K to the half "
                    "marathon in 2027. Lighter training in Nov–Dec for family time.",
            "start": days[0]["date"],
            "end": days[-1]["date"],
            "totalDays": len(days),
            "timeTrialMiles": tt_miles,
            "readme": meta_rows,
            "rotation": rotation,
            "zonesNote": zones_note,
        },
        "days": days,
        "weeks": weeks,
        "zones": zones,
        "kbLevels": kb,
    }

    with open(OUT_JSON, "w") as fh:
        json.dump(plan, fh, indent=2)

    with open(OUT_JS, "w") as fh:
        fh.write("// Generated by scripts/build_plan.py — do not edit by hand.\n")
        fh.write("window.PLAN = ")
        json.dump(plan, fh, separators=(",", ":"))
        fh.write(";\n")

    print(f"days={len(days)} weeks={len(weeks)} zones={len(zones)} kb={len(kb)}")
    print("first day:", days[0]["date"], days[0]["weekday"], "|", days[0]["session"])
    print("last day: ", days[-1]["date"], days[-1]["weekday"], "|", days[-1]["session"])


if __name__ == "__main__":
    main()
