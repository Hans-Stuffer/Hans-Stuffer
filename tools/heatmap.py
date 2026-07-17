#!/usr/bin/env python3
"""Render a commit heatmap from local repos, dates only.

Reads nothing but commit timestamps. No messages, no paths, no diffs, no code.
Regenerate with:  python3 tools/heatmap.py
Then paste the output between the HEATMAP markers in README.md.
"""
import subprocess, datetime as dt
from collections import Counter

EMAILS = [
    "hansstuffer@pop-os.lan",
    "stuffer.hans2219@gmail.com",
    "103386122+Hans-Stuffer@users.noreply.github.com",
]
REPOS = [
    "/Users/hansstuffer/dev/Chooseout",
    "/Users/hansstuffer/plexus",
    "/Users/hansstuffer/physics",
    "/Users/hansstuffer/dev/Hans-Stuffer",
]
SINCE = dt.date(2026, 2, 1)
PALETTE = "·░▒▓█"


def collect():
    counts = Counter()
    for repo in REPOS:
        cmd = ["git", "-C", repo, "log", "--no-merges",
               f"--since={SINCE}", "--format=%ad", "--date=short"]
        cmd += [f"--author={e}" for e in EMAILS]
        out = subprocess.run(cmd, capture_output=True, text=True).stdout
        for line in out.split("\n"):
            if line.strip():
                counts[line.strip()] += 1
    return counts


def level(n):
    if n == 0: return 0
    if n <= 2: return 1
    if n <= 5: return 2
    if n <= 10: return 3
    return 4


def render(counts, end):
    start = SINCE - dt.timedelta(days=(SINCE.weekday() + 1) % 7)
    weeks, cur = [], start
    while cur <= end:
        col = []
        for i in range(7):
            d = cur + dt.timedelta(days=i)
            col.append(counts.get(d.isoformat(), 0) if SINCE <= d <= end else None)
        weeks.append((cur, col))
        cur += dt.timedelta(days=7)

    header, last = "", None
    for w, _ in weeks:
        m = (w + dt.timedelta(days=6)).strftime("%b").lower()
        header += m[0] if m != last else " "
        last = m

    lines = ["    " + header]
    for row, label in enumerate(["   ", "mon", "   ", "wed", "   ", "fri", "   "]):
        cells = "".join(
            PALETTE[level(w[1][row])] if w[1][row] is not None else " " for w in weeks
        )
        lines.append(f"{label} {cells}")
    return "\n".join(lines)


if __name__ == "__main__":
    counts = collect()
    end = dt.date.today()
    span = (end - SINCE).days
    print(render(counts, end))
    print()
    print(f"    {sum(counts.values())} commits · {len(counts)} active days of {span}")
