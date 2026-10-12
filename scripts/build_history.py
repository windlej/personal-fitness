#!/usr/bin/env python3
"""Distill a Strava / SmashRun activity export into a coach-readable summary.

Usage:
    python3 scripts/build_history.py [CSV] [--unit auto|km|mi|m]

[CSV] is optional. If omitted, the script looks (in the repo root) for:
    history.csv, smashrun-export.csv, activities.csv, strava/activities.csv

It writes:
    docs/training-history.md   <- the digest the training-coach agent reads
    data/history-summary.json  <- the same numbers, machine-readable

The input may be Strava's bulk-export ``activities.csv`` or the CSV from
SmashRun (append ``/export`` to your SmashRun URL). Columns are detected by
name, so minor differences are fine. Run it once and read the printed report;
if a column can't be found, pass --unit or rename the CSV column.

The raw export is personal (dates, heart rate). It is git-ignored; never commit
it to this public repo.
"""

import csv
import datetime as dt
import json
import os
import re
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT_MD = os.path.join(ROOT, "docs", "training-history.md")
OUT_JSON = os.path.join(ROOT, "data", "history-summary.json")

SEARCH = ["history.csv", "smashrun-export.csv", "activities.csv",
          os.path.join("strava", "activities.csv")]

RUN_TYPES = {"run", "running", "trailrun", "trail run", "treadmill",
             "virtualrun", "virtual run", "race", "walk"}

DISTANCE_TARGETS = {"5K": 5.0, "10K": 10.0, "Half (13.1)": 21.0975,
                    "Marathon (26.2)": 42.195}


# --------------------------------------------------------------------------- #
# parsing helpers
# --------------------------------------------------------------------------- #

def find_col(headers, *needles, exclude=()):
    """Return the first header containing any needle (case-insensitive)."""
    for h in headers:
        hl = h.lower()
        if any(n in hl for n in needles) and not any(x in hl for x in exclude):
            return h
    return None


def parse_date(value):
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        return dt.datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        pass
    for fmt in ("%b %d, %Y, %I:%M:%S %p", "%b %d, %Y %I:%M:%S %p",
                "%b %d, %Y, %H:%M:%S", "%b %d, %Y",
                "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d",
                "%m/%d/%Y %H:%M:%S", "%m/%d/%Y", "%d/%m/%Y"):
        try:
            return dt.datetime.strptime(text, fmt)
        except ValueError:
            continue
    m = re.search(r"(\d{4})-(\d{2})-(\d{2})", text)
    if m:
        return dt.datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    return None


def parse_duration(value):
    """Return seconds. Handles seconds, minutes, and 'H:MM:SS' / 'MM:SS'."""
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    if ":" in text:
        parts = [int(p) for p in re.findall(r"\d+", text)]
        while len(parts) < 3:
            parts.insert(0, 0)
        h, m, s = parts[-3], parts[-2], parts[-1]
        return h * 3600 + m * 60 + s
    try:
        num = float(re.sub(r"[^0-9.]", "", text) or "nan")
    except ValueError:
        return None
    if num != num:  # NaN
        return None
    return num * 60 if num < 500 else num  # crude min vs seconds heuristic


def parse_distance_km(value, mode):
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    factor = None
    low = text.lower()
    if "km" in low:
        factor = 1.0
    elif "mi" in low:
        factor = 1.60934
    try:
        num = float(re.sub(r"[^0-9.]", "", text) or "nan")
    except ValueError:
        return None
    if num != num:
        return None
    if factor is not None:
        return num * factor
    if mode == "m":
        return num / 1000.0
    if mode == "mi":
        return num * 1.60934
    if mode == "km":
        return num
    return num / 1000.0 if num > 100 else num  # auto: >100 assumed metres


def fmt_hours(seconds):
    return "%.1f hours" % (seconds / 3600.0) if seconds else "0 hours"


def pace_str(seconds, km):
    if not seconds or not km:
        return "—"
    sec_per_km = seconds / km
    m = int(sec_per_km // 60)
    s = int(round(sec_per_km % 60))
    if s == 60:
        m, s = m + 1, 0
    return "%d:%02d /km" % (m, s)


# --------------------------------------------------------------------------- #
# load
# --------------------------------------------------------------------------- #

def resolve_input(argv):
    args = [a for a in argv if not a.startswith("--")]
    unit = "auto"
    for a in argv:
        if a.startswith("--unit"):
            unit = a.split("=", 1)[1] if "=" in a else "auto"
    if args and args[0] not in ("auto", "km", "mi", "m"):
        path = args[0]
    else:
        path = next((p for p in SEARCH
                     if os.path.exists(os.path.join(ROOT, p))), None)
    return path, unit


def load_activities(path, unit):
    with open(path, newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        return [], {}
    headers = list(rows[0].keys())
    cols = {
        "date": find_col(headers, "activity date", "start time", "starttime",
                         "date", "start"),
        "distance": find_col(headers, "distance", "dist"),
        "duration": find_col(headers, "moving time", "movingtime", "duration",
                             "elapsed time", "time", exclude=("date", "start")),
        "type": find_col(headers, "activity type", "type", "sport"),
        "hr": find_col(headers, "average heart", "avg heart", "average hr",
                       "heart rate", "avg hr", "heartrate"),
    }
    print("Detected columns:")
    for key, val in cols.items():
        print("  %-9s -> %s" % (key, val))
    if not cols["date"] or not cols["distance"]:
        print("\nCould not find date/distance columns. Headers were:")
        print("  " + ", ".join(headers))
        print("Rename the columns or pass a different CSV.")
        sys.exit(2)

    acts = []
    for r in rows:
        if cols["type"]:
            t = (r.get(cols["type"]) or "").strip().lower()
            if t and t not in RUN_TYPES:
                continue
        date = parse_date(r.get(cols["date"]))
        km = parse_distance_km(r.get(cols["distance"]), unit)
        secs = parse_duration(r.get(cols["duration"])) if cols["duration"] else None
        if date is None or km is None or km <= 0:
            continue
        acts.append({
            "date": date,
            "km": km,
            "secs": secs,
            "hr": _num(r.get(cols["hr"])) if cols["hr"] else None,
        })
    acts.sort(key=lambda a: a["date"])
    return acts, cols


def _num(v):
    try:
        f = float(re.sub(r"[^0-9.]", "", str(v)) or "nan")
        return None if f != f else f
    except (ValueError, TypeError):
        return None


# --------------------------------------------------------------------------- #
# analysis
# --------------------------------------------------------------------------- #

def week_start(d):
    return (d - dt.timedelta(days=d.weekday())).date()


def analyse(acts):
    dates = [a["date"] for a in acts]
    total_km = sum(a["km"] for a in acts)
    total_secs = sum(a["secs"] or 0 for a in acts)
    start, end = min(dates), max(dates)
    span_days = (end.date() - start.date()).days

    weeks = sorted({week_start(d) for d in dates})
    total_weeks = span_days // 7 + 1
    week_set = set(weeks)

    streaks, run = [], 1
    for i in range(1, len(weeks)):
        if (weeks[i] - weeks[i - 1]).days == 7:
            run += 1
        else:
            streaks.append(run)
            run = 1
    streaks.append(run)
    longest_streak = max(streaks) if streaks else 0
    # current streak: consecutive weeks ending at the latest activity week
    current = 0
    w = weeks[-1]
    while w in week_set:
        current += 1
        w = w - dt.timedelta(days=7)

    gaps = [(dates[i] - dates[i - 1]).days for i in range(1, len(dates))]
    longest_gap = max(gaps) if gaps else 0

    dow = [0] * 7
    for d in dates:
        dow[d.weekday()] += 1

    by_year = {}
    for a in acts:
        y = a["date"].year
        e = by_year.setdefault(y, {"n": 0, "km": 0.0, "secs": 0.0, "longest": 0.0})
        e["n"] += 1
        e["km"] += a["km"]
        e["secs"] += a["secs"] or 0
        e["longest"] = max(e["longest"], a["km"])

    prs = {}
    if any(a["secs"] for a in acts):
        for label, target in DISTANCE_TARGETS.items():
            best = None
            for a in acts:
                if not a["secs"]:
                    continue
                if abs(a["km"] - target) <= target * 0.02:
                    if best is None or a["secs"] < best["secs"]:
                        best = a
            if best:
                prs[label] = {"date": best["date"].date().isoformat(),
                              "km": round(best["km"], 2),
                              "secs": best["secs"],
                              "pace": pace_str(best["secs"], best["km"])}

    paced = [a for a in acts if a["secs"] and a["km"]]
    avg_pace = (pace_str(statistics.mean(a["secs"] / a["km"] for a in paced), 1)
                if paced else "—")

    return {
        "count": len(acts), "total_km": total_km, "total_secs": total_secs,
        "first": start.date().isoformat(), "last": end.date().isoformat(),
        "span_days": span_days, "total_weeks": total_weeks,
        "pct_weeks_running": 100.0 * len(weeks) / total_weeks if total_weeks else 0,
        "longest_streak_weeks": longest_streak, "current_streak_weeks": current,
        "longest_gap_days": longest_gap,
        "avg_runs_per_week": len(acts) / total_weeks if total_weeks else 0,
        "avg_km_per_week": total_km / total_weeks if total_weeks else 0,
        "avg_pace": avg_pace, "dow": dow, "by_year": by_year, "prs": prs,
    }


# --------------------------------------------------------------------------- #
# render
# --------------------------------------------------------------------------- #

def render(stats, cols, source):
    DOW = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    lines = []
    A = lines.append
    A("# Training history (from Strava / SmashRun)")
    A("")
    A("_Generated by `scripts/build_history.py` from `%s`. "
      "Re-run it after exporting fresh data. Numbers are approximate — the "
      "source CSV is a summary, not per-second data._" % source)
    A("")
    A("## All-time")
    A("")
    A("| Metric | Value |")
    A("|--------|-------|")
    A("| Runs logged | %d |" % stats["count"])
    A("| Total distance | %.0f km |" % stats["total_km"])
    A("| Total moving time | %s |" % fmt_hours(stats["total_secs"]))
    A("| Date range | %s → %s (%.1f years) |"
      % (stats["first"], stats["last"], stats["span_days"] / 365.25))
    A("| Average run pace | %s |" % stats["avg_pace"])
    A("| Average volume | %.1f km/week over %.1f runs/week |"
      % (stats["avg_km_per_week"], stats["avg_runs_per_week"]))
    A("")
    A("## Consistency")
    A("")
    A("| Metric | Value |")
    A("|--------|-------|")
    A("| Weeks with at least one run | %.0f%% |" % stats["pct_weeks_running"])
    A("| Longest streak (consecutive weeks running) | %d weeks |"
      % stats["longest_streak_weeks"])
    A("| Current streak | %d weeks |" % stats["current_streak_weeks"])
    A("| Longest break between runs | %d days |" % stats["longest_gap_days"])
    busiest = DOW[max(range(7), key=lambda i: stats["dow"][i])]
    A("| Favourite running day | %s |" % busiest)
    A("")
    A("Runs by weekday: " + ", ".join(
        "%s %d" % (DOW[i], stats["dow"][i]) for i in range(7)) + ".")
    A("")

    A("## Personal bests (from matched-distance runs)")
    A("")
    if stats["prs"]:
        A("| Distance | Time | Pace | Date |")
        A("|----------|------|------|------|")
        for label, pr in stats["prs"].items():
            A("| %s | %s | %s | %s |"
              % (label, _hms(pr["secs"]), pr["pace"], pr["date"]))
    else:
        A("No single runs closely matched standard race distances.")
    A("")

    A("## By year")
    A("")
    A("| Year | Runs | Distance | Hours | Avg km/wk | Longest run |")
    A("|------|------|----------|-------|-----------|-------------|")
    for y in sorted(stats["by_year"], reverse=True):
        e = stats["by_year"][y]
        wk = 52.0
        A("| %d | %d | %.0f km | %.1f | %.1f | %.1f km |"
          % (y, e["n"], e["km"], e["secs"] / 3600.0, e["km"] / wk, e["longest"]))
    A("")

    A("## Insights for the coach")
    A("")
    ins = []
    if stats["current_streak_weeks"] >= 4:
        ins.append("Currently consistent — %d weeks running without a gap."
                   % stats["current_streak_weeks"])
    elif stats["longest_gap_days"] >= 21:
        ins.append("History includes long breaks (up to %d days) — plan for "
                   "restarts and rebuild gradually." % stats["longest_gap_days"])
    ins.append("Typical week is about %.0f km over %.1f runs."
               % (stats["avg_km_per_week"], stats["avg_runs_per_week"]))
    best_year = max(stats["by_year"], key=lambda y: stats["by_year"][y]["km"])
    ins.append("Biggest recent-volume year on record: %d (%.0f km)."
               % (best_year, stats["by_year"][best_year]["km"]))
    ins.append("Average easy-ish pace across all runs: %s." % stats["avg_pace"])
    for line in ins:
        A("- " + line)
    A("")
    return "\n".join(lines) + "\n"


def _hms(secs):
    h = secs // 3600
    m = (secs % 3600) // 60
    s = secs % 60
    return ("%d:%02d:%02d" % (h, m, s)) if h else ("%d:%02d" % (m, s))


def main():
    path, unit = resolve_input(sys.argv[1:])
    if not path or not os.path.exists(os.path.join(ROOT, path)):
        print("No input CSV found. Looked for: " + ", ".join(SEARCH))
        print("Usage: python3 scripts/build_history.py path/to/export.csv [--unit km|mi|m]")
        sys.exit(2)

    acts, cols = load_activities(os.path.join(ROOT, path), unit)
    if not acts:
        print("No running activities found in %s." % path)
        sys.exit(2)

    stats = analyse(acts)
    md = render(stats, cols, path)
    with open(OUT_MD, "w") as fh:
        fh.write(md)
    with open(OUT_JSON, "w") as fh:
        json.dump(stats, fh, indent=2, default=str)

    print("\n%d runs, %.0f km, %s -> %s"
          % (stats["count"], stats["total_km"], stats["first"], stats["last"]))
    print("Wrote %s and %s"
          % (os.path.relpath(OUT_MD, ROOT), os.path.relpath(OUT_JSON, ROOT)))


if __name__ == "__main__":
    main()
