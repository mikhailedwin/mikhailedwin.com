#!/usr/bin/env python3
"""
update_bonds.py — sovereign yields for the header ticker.

The page is static and lives on GitHub Pages, so it cannot reach these
sources itself: the Treasury sends no CORS headers and FRED sits behind
a bot wall. This runs on a schedule instead and commits a small JSON
file the page can read from its own origin.

Sources
  US 3Y / 5Y / 10Y   Daily Treasury Par Yield Curve, official CSV, daily
  CN 10Y             FRED IRLTLT01CNM156N, monthly
  IN 10Y             FRED INDIRLTLT01STM, monthly

Any leg that fails keeps its last known value and is flagged stale, so a
single bad source degrades one row rather than emptying the ticker.
"""

import csv
import io
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "bonds.json")

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")

TREASURY = ("https://home.treasury.gov/resource-center/data-chart-center/"
            "interest-rates/daily-treasury-rates.csv/{year}/all"
            "?type=daily_treasury_yield_curve"
            "&field_tdr_date_value={year}&page&_format=csv")

FRED = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}"

# label -> (source kind, key)
US_LEGS = [("US3Y", "3 Yr"), ("US5Y", "5 Yr"), ("US10Y", "10 Yr")]
FRED_LEGS = [("CN10Y", "IRLTLT01CNM156N"), ("IN10Y", "INDIRLTLT01STM")]


def fetch(url, tries=3):
    """GET with retries. Returns text, or None once the attempts run out."""
    for n in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as r:
                body = r.read().decode("utf-8", "replace")
            if body.strip() and "<html" not in body[:400].lower():
                return body
        except (urllib.error.URLError, OSError) as e:
            print("  fetch failed (%s/%s): %s" % (n + 1, tries, e), file=sys.stderr)
        time.sleep(3 * (n + 1))
    return None


def load_previous():
    try:
        with open(OUT) as f:
            return {r["sym"]: r for r in json.load(f).get("rows", [])}
    except (OSError, ValueError, KeyError):
        return {}


def us_yields():
    """Latest two rows of the par yield curve, so we get a daily change."""
    year = datetime.now(timezone.utc).year
    body = fetch(TREASURY.format(year=year))
    if not body:
        # First trading days of January can be empty; fall back a year.
        body = fetch(TREASURY.format(year=year - 1))
    if not body:
        return {}, None

    rows = list(csv.DictReader(io.StringIO(body)))
    if not rows:
        return {}, None

    # The file is newest first, but do not rely on it.
    def key(r):
        try:
            return datetime.strptime(r["Date"], "%m/%d/%Y")
        except (ValueError, KeyError):
            return datetime.min

    rows.sort(key=key, reverse=True)
    latest, prior = rows[0], rows[1] if len(rows) > 1 else None

    out = {}
    for sym, col in US_LEGS:
        try:
            now = float(latest[col])
        except (KeyError, TypeError, ValueError):
            continue
        chg = None
        if prior:
            try:
                chg = round(now - float(prior[col]), 3)
            except (KeyError, TypeError, ValueError):
                chg = None
        out[sym] = {"val": round(now, 3), "chg": chg}
    return out, latest.get("Date")


def fred_yield(sid):
    """Last two observations of a FRED series."""
    body = fetch(FRED.format(sid=sid))
    if not body:
        return None
    pts = []
    for row in csv.reader(io.StringIO(body)):
        if len(row) < 2 or row[0] in ("DATE", "observation_date"):
            continue
        try:
            pts.append((row[0], float(row[1])))
        except ValueError:
            continue          # FRED writes '.' for missing observations
    if not pts:
        return None
    date, now = pts[-1]
    chg = round(now - pts[-2][1], 3) if len(pts) > 1 else None
    return {"val": round(now, 3), "chg": chg, "asof": date}


def main():
    prev = load_previous()
    rows = []

    print("US treasury par yield curve")
    us, us_date = us_yields()
    for sym, _ in US_LEGS:
        if sym in us:
            rows.append(dict(sym=sym, asof=us_date, stale=False, **us[sym]))
            print("  %-6s %s" % (sym, us[sym]["val"]))
        elif sym in prev:
            rows.append(dict(prev[sym], stale=True))
            print("  %-6s kept last known" % sym)

    for sym, sid in FRED_LEGS:
        print("FRED %s (%s)" % (sym, sid))
        got = fred_yield(sid)
        if got:
            rows.append(dict(sym=sym, stale=False, **got))
            print("  %-6s %s" % (sym, got["val"]))
        elif sym in prev:
            rows.append(dict(prev[sym], stale=True))
            print("  %-6s kept last known" % sym)
        else:
            print("  %-6s no data and nothing cached, skipping" % sym)

    if not rows:
        print("every source failed, leaving the existing file alone", file=sys.stderr)
        return 1

    payload = {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "rows": rows,
    }
    with open(OUT, "w") as f:
        json.dump(payload, f, indent=1)
        f.write("\n")
    print("wrote %s with %d rows" % (OUT, len(rows)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
