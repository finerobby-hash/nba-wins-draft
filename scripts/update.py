#!/usr/bin/env python3
"""Fetch current NBA standings and refresh data/standings.json + data/history.json.

Runs daily via GitHub Actions. Source: ESPN's public standings feed.
"""
import json, sys, datetime, urllib.request, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
ESPN = "https://site.api.espn.com/apis/v2/sports/basketball/nba/standings"
ESPN_ABBR = {"GS": "GSW", "NO": "NOP", "NY": "NYK", "SA": "SAS", "UTAH": "UTA", "WSH": "WAS", "PHO": "PHX"}

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (wins-draft-tracker)"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

def parse_espn(payload):
    out = {}
    groups = payload.get("children") or [payload]
    for g in groups:
        for e in (g.get("standings") or {}).get("entries", []):
            ab = e["team"]["abbreviation"].upper()
            ab = ESPN_ABBR.get(ab, ab)
            w = l = None
            for s in e.get("stats", []):
                if s.get("name") == "wins": w = int(s["value"])
                if s.get("name") == "losses": l = int(s["value"])
            if w is not None and l is not None:
                out[ab] = (w, l)
    return out

def main():
    cfg = json.load(open(ROOT / "config.json"))
    standings_path = ROOT / "data" / "standings.json"
    history_path = ROOT / "data" / "history.json"
    old = json.load(open(standings_path))
    old_map = {t["abbr"]: (t["wins"], t["losses"]) for t in old["teams"]}

    try:
        records = parse_espn(fetch(ESPN))
    except Exception as ex:
        print("ESPN fetch failed:", ex, file=sys.stderr)
        sys.exit(1)

    missing = [t["abbr"] for t in cfg["teams"] if t["abbr"] not in records]
    if missing:
        print("Missing teams from feed:", missing, file=sys.stderr)
        sys.exit(1)

    # Sanity: records should never go backwards.
    for ab, (w, l) in records.items():
        ow, ol = old_map.get(ab, (0, 0))
        if w < ow or l < ol:
            print(f"Refusing update: {ab} went backwards ({ow}-{ol} -> {w}-{l})", file=sys.stderr)
            sys.exit(1)

    now = datetime.datetime.now(datetime.timezone.utc)
    new = {
        "updated": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": "ESPN standings feed",
        "teams": [{"abbr": t["abbr"], "wins": records[t["abbr"]][0], "losses": records[t["abbr"]][1]} for t in cfg["teams"]],
    }
    json.dump(new, open(standings_path, "w"), indent=1)

    # Snapshot per owner for the history chart (one row per owner per day; today overwrites).
    lines = cfg["lines"]
    owner_of = {t["abbr"]: t["owner"] for t in cfg["teams"]}
    agg = {}
    for t in new["teams"]:
        o = owner_of[t["abbr"]]
        w, l = t["wins"], t["losses"]
        proj = w + lines[t["abbr"]] / 82 * (82 - w - l)
        a = agg.setdefault(o, {"wins": 0, "losses": 0, "proj": 0.0})
        a["wins"] += w; a["losses"] += l; a["proj"] += proj
    today = now.strftime("%Y-%m-%d")
    hist = [h for h in json.load(open(history_path)) if h["date"] != today]
    for o in cfg["owners"]:
        a = agg[o["name"]]
        hist.append({"date": today, "owner": o["name"], "wins": a["wins"], "losses": a["losses"], "proj": round(a["proj"], 1)})
    hist.sort(key=lambda h: (h["date"], h["owner"]))
    json.dump(hist, open(history_path, "w"), indent=0)
    changed = sum(1 for ab, r in records.items() if old_map.get(ab) != r)
    print(f"Updated {changed} team records; snapshot {today} written.")

if __name__ == "__main__":
    main()
