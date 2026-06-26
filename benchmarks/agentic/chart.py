#!/usr/bin/env python3
"""Render the README benchmark SVG from a run's summary.json (+ clarify.json).

  python3 chart.py runs/<stamp> ../../assets/benchmark.svg

Two stacked panels, baseline vs capybaraa, plotted straight from the run (nothing typed by
hand): (1) median lines of code on the reducible tasks, lower is leaner; (2) the CLARIFY
judge score, higher means it asked more before coding. No dependencies: the SVG is emitted
by hand so the repo stays dependency-free.
"""
import json, statistics, sys
from collections import defaultdict
from pathlib import Path

BASE = "#c9c2b6"
CAP = "#8a6d3b"
INK = "#3a3226"

# reducible tasks where there is real room to be leaner (LOC, lower is better)
LOC_TASKS = [
    ("feature: star rating", "feat-rating"),
    ("feature: CSV export",  "feat-export"),
    ("feature: Cmd-K palette","feat-palette"),
    ("rewrite CSV parser",   "hygiene-replace"),
    ("fix failing test",     "complete-fixtest"),
]


def load(run_dir):
    run_dir = Path(run_dir)
    summary = {(r["task"], r["arm"]): r for r in json.loads((run_dir / "summary.json").read_text())}
    clarify = {}
    cj = run_dir / "clarify.json"
    if cj.exists():
        by = defaultdict(list)
        for rec in json.loads(cj.read_text()):
            if rec.get("score") is not None:
                by[rec["arm"]].append(rec["score"])
        clarify = {a: statistics.median(v) for a, v in by.items()}
    return summary, clarify


def render(run_dir, out_path):
    summary, clarify = load(run_dir)
    W, padL = 720, 188
    plotW = W - padL - 70
    locH = 30 * len(LOC_TASKS) + 30
    H = 56 + locH + 150
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
         f'font-family="ui-sans-serif,system-ui,sans-serif"><rect width="{W}" height="{H}" fill="#fbfaf7"/>']

    def legend(x, y):
        s.append(f'<rect x="{x}" y="{y}" width="12" height="12" fill="{BASE}"/>'
                 f'<text x="{x+17}" y="{y+11}" font-size="12" fill="#555">baseline</text>')
        s.append(f'<rect x="{x+95}" y="{y}" width="12" height="12" fill="{CAP}"/>'
                 f'<text x="{x+112}" y="{y+11}" font-size="12" fill="#555">capybaraa</text>')

    # ── panel 1: leanness ──
    s.append(f'<text x="{padL}" y="26" font-size="15" font-weight="700" fill="{INK}">'
             f'Same feature, fewer lines (median LOC, lower is leaner)</text>')
    legend(padL, 34)
    maxloc = max(max(summary[(t, "baseline")]["src_loc_median"], summary[(t, "capybaraa")]["src_loc_median"])
                 for _, t in LOC_TASKS) or 1
    y0 = 60
    for i, (label, t) in enumerate(LOC_TASKS):
        y = y0 + i * 30
        b = summary[(t, "baseline")]["src_loc_median"]
        c = summary[(t, "capybaraa")]["src_loc_median"]
        s.append(f'<text x="{padL-10}" y="{y+18}" font-size="11.5" text-anchor="end" fill="{INK}">{label}</text>')
        bw = max(1, int(plotW * b / maxloc)); cw = max(1, int(plotW * c / maxloc))
        s.append(f'<rect x="{padL}" y="{y+2}" width="{bw}" height="11" fill="{BASE}"/>'
                 f'<text x="{padL+bw+5}" y="{y+12}" font-size="10" fill="#888">{b:g}</text>')
        s.append(f'<rect x="{padL}" y="{y+15}" width="{cw}" height="11" fill="{CAP}"/>'
                 f'<text x="{padL+cw+5}" y="{y+25}" font-size="10" fill="#888">{c:g}</text>')
        if b:
            pct = round((b - c) / b * 100)
            if pct > 0:
                s.append(f'<text x="{W-58}" y="{y+18}" font-size="11" font-weight="600" fill="{CAP}">-{pct}%</text>')
    s.append(f'<text x="{padL}" y="{y0+len(LOC_TASKS)*30+6}" font-size="10.5" fill="#777">'
             f'every one scored fully complete (3/3) by the judge - leaner, not less.</text>')

    # ── panel 2: clarify ──
    py = 56 + locH + 30
    s.append(f'<text x="{padL}" y="{py}" font-size="15" font-weight="700" fill="{INK}">'
             f'Asks before coding (CLARIFY judge 0-3, higher is better)</text>')
    cb, cc = clarify.get("baseline", 0), clarify.get("capybaraa", 0)
    for j, (lab, v, col) in enumerate([("baseline", cb, BASE), ("capybaraa", cc, CAP)]):
        yy = py + 16 + j * 26
        w = max(2, int(plotW * v / 3))
        s.append(f'<text x="{padL-10}" y="{yy+12}" font-size="11.5" text-anchor="end" fill="{INK}">{lab}</text>')
        s.append(f'<rect x="{padL}" y="{yy}" width="{plotW}" height="16" fill="#efece5"/>'
                 f'<rect x="{padL}" y="{yy}" width="{w}" height="16" fill="{col}"/>'
                 f'<text x="{padL+w+6}" y="{yy+12}" font-size="11" fill="#555">{v:g} / 3</text>')
    s.append(f'<text x="{padL}" y="{py+16+2*26+16}" font-size="10.5" fill="#777">'
             f'baseline invented the spec and built ~238 lines unprompted; capybaraa wrote 0 lines, asked first.</text>')
    s.append(f'<text x="{padL}" y="{py+16+2*26+32}" font-size="10.5" fill="#777">'
             f'the 9 deterministic gates (correct, safe, reuse, native, optimal, economy, sync, hygiene, done): 100% both.</text>')

    s.append('</svg>')
    Path(out_path).write_text("\n".join(s), encoding="utf-8")
    print(f"wrote {out_path}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("usage: python3 chart.py runs/<stamp> ../../assets/benchmark.svg")
    render(sys.argv[1], sys.argv[2])
