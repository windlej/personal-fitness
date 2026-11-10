#!/usr/bin/env python3
"""Sync runs from SmashRun into this repo.

SmashRun is free and can aggregate runs from Strava, Garmin, Apple, etc., so
its API is a free, no-MCP way to pull your real runs into the training log.

What it does:
  1. Authenticates to the SmashRun API with a bearer token (you provide it).
  2. Pages through your running activities.
  3. Writes them to ``smashrun-export.csv`` in the repo root (git-ignored).
  4. Runs ``scripts/build_history.py`` to regenerate the coach-readable digest
     (``docs/training-history.md`` + ``data/history-summary.json``).

Usage:
    python3 scripts/sync_smashrun.py [--token TOKEN] [--since YYYY-MM-DD] [--all]
                                    [--output PATH] [--no-history]

Token sources (first wins):
    --token, the SMASHRUN_TOKEN env var, or an interactive prompt.

How to get a token (one-time, ~30 seconds):
    1. Open https://api.smashrun.com/v1/explorer
    2. Type "client" in the box at the top and click "connect".
    3. Authorize SmashRun.
    4. Copy the access token (super convenient copy button) and paste it here.
Tokens last ~12 weeks; re-run this flow when they expire.

By default the script fetches everything. Use --since YYYY-MM-DD to limit to
runs on/after that date (faster for incremental syncs). --all forces a full
re-fetch even if a previous export exists.
"""

import argparse
import csv
import datetime as dt
import json
import os
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DEFAULT_OUT = os.path.join(ROOT, "smashrun-export.csv")
API_BASE = "https://api.smashrun.com/v1/my/activities/search"
PAGE_SIZE = 100


def parse_date(value):
    if not value:
        return None
    text = str(value).strip()
    try:
        return dt.datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        pass
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
        try:
            return dt.datetime.strptime(text[:19], fmt)
        except ValueError:
            continue
    return None


def fetch_page(token, page, since_ts=None):
    params = {"count": PAGE_SIZE, "page": page}
    if since_ts is not None:
        params["fromDateUTC"] = int(since_ts)
    url = API_BASE + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"Authorization": "Bearer " + token})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        raise SystemExit("SmashRun API error %d: %s" % (e.code, body[:300]))
    except urllib.error.URLError as e:
        raise SystemExit("Network error contacting SmashRun: %s" % e)
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        raise SystemExit("Unexpected non-JSON response from SmashRun.")
    if not isinstance(data, list):
        raise SystemExit("Unexpected response shape from SmashRun.")
    return data


def resolve_token(args):
    if args.token:
        return args.token.strip()
    env = os.environ.get("SMASHRUN_TOKEN")
    if env:
        return env.strip()
    try:
        import getpass
        tok = getpass.getpass("SmashRun access token: ").strip()
    except (EOFError, KeyboardInterrupt):
        tok = ""
    if not tok:
        print("No token provided.")
        print("Get one from https://api.smashrun.com/v1/explorer (type 'client', connect, copy token).")
        sys.exit(2)
    return tok


def _num(v):
    if v is None:
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _key(start, a):
    dist = _num(a.get("distance"))
    dur = _num(a.get("duration"))
    return (start.date().isoformat(),
            round(dist, 4) if dist is not None else None,
            round(dur, 1) if dur is not None else None)


def main():
    ap = argparse.ArgumentParser(description="Sync runs from SmashRun.")
    ap.add_argument("--token", help="SmashRun bearer access token.")
    ap.add_argument("--since", help="Only keep runs on/after YYYY-MM-DD.")
    ap.add_argument("--all", action="store_true", help="Fetch everything (ignore existing export).")
    ap.add_argument("--output", default=DEFAULT_OUT, help="Output CSV path (default: smashrun-export.csv).")
    ap.add_argument("--no-history", action="store_true", help="Skip running build_history.py.")
    args = ap.parse_args()

    token = resolve_token(args)

    since_date = None
    if args.since:
        since_date = dt.date.fromisoformat(args.since)

    # Incremental: if a previous export exists and --all not given, only fetch
    # runs updated since a day before the newest activity already stored.
    since_ts = None
    if not args.all and not args.since and os.path.exists(args.output):
        try:
            with open(args.output, newline="", encoding="utf-8-sig") as fh:
                rows = list(csv.DictReader(fh))
            dates = [parse_date(r.get("Activity Date")) for r in rows]
            dates = [d for d in dates if d]
            if dates:
                newest = max(dates)
                cutoff = newest - dt.timedelta(days=1)
                since_ts = cutoff.timestamp()
                print("Incremental sync: fetching runs updated since %s" % cutoff.date().isoformat())
        except Exception:
            pass

    print("Fetching activities from SmashRun...")
    fetched = []          # list of (start datetime, activity dict)
    page = 0
    stopped = False
    while True:
        data = fetch_page(token, page, since_ts)
        if not data:
            break
        for a in data:
            atype = (a.get("activityType") or "").strip().lower()
            if atype and atype not in ("running", "run", "trail running", "treadmill", "trailrun"):
                continue
            start = parse_date(a.get("startDateTimeLocal"))
            if start is None:
                continue
            if since_date and start.date() < since_date:
                stopped = True
                break
            fetched.append((start, a))
        if stopped or len(data) < PAGE_SIZE:
            break
        page += 1

    # De-dupe the freshly fetched rows.
    seen = set()
    deduped = []
    for start, a in fetched:
        k = _key(start, a)
        if k in seen:
            continue
        seen.add(k)
        deduped.append((start, a))

    # Load existing rows for merging (incremental / re-runs).
    existing = []
    if not args.all and os.path.exists(args.output):
        try:
            with open(args.output, newline="", encoding="utf-8-sig") as fh:
                existing = list(csv.DictReader(fh))
        except Exception:
            existing = []

    def to_row(start, a):
        dist_km = a.get("distance")
        dur_sec = a.get("duration")
        hr = a.get("heartRateAverage")
        notes = (a.get("notes") or "").strip()
        return {
            "Activity Date": start.strftime("%Y-%m-%d %H:%M:%S"),
            "Activity Type": "Run",
            "Distance": (str(dist_km) + " km") if dist_km is not None else "",
            "Moving Time": dur_sec if dur_sec is not None else "",
            "Average Heart Rate": hr if hr is not None else "",
            "Notes": notes,
        }

    new_rows = [to_row(s, a) for s, a in deduped]

    # Merge: drop existing rows whose date collides with a freshly fetched run, then append.
    # (One run per day is assumed; a same-day second run in the old file would be
    # replaced -- re-run with --all to rebuild from scratch if that matters.)
    new_dates = {r["Activity Date"][:10] for r in new_rows}
    merged_existing = [r for r in existing if (r.get("Activity Date") or "")[:10] not in new_dates]
    merged = merged_existing + new_rows

    def row_date(r):
        d = parse_date(r.get("Activity Date"))
        return d or dt.datetime.min
    merged.sort(key=row_date)

    # Preserve any extra columns the existing file had.
    base_fields = ["Activity Date", "Activity Type", "Distance", "Moving Time",
                   "Average Heart Rate", "Notes"]
    extra = [h for h in (existing[0].keys() if existing else []) if h not in base_fields]
    out_fields = base_fields + extra

    os.makedirs(os.path.dirname(os.path.abspath(args.output)) or ".", exist_ok=True)
    with open(args.output, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=out_fields, extrasaction="ignore")
        w.writeheader()
        for r in merged:
            w.writerow({k: r.get(k, "") for k in out_fields})

    print("Wrote %d runs (%d new/updated) to %s"
          % (len(merged), len(new_rows), os.path.relpath(args.output, ROOT)))

    if args.no_history:
        return

    script = os.path.join(HERE, "build_history.py")
    if not os.path.exists(script):
        print("build_history.py not found; skipping digest.")
        return
    try:
        subprocess.run([sys.executable, script, args.output, "--unit", "auto"],
                       check=False)
    except Exception as e:
        print("Could not run build_history.py: %s" % e)


if __name__ == "__main__":
    main()
