#!/usr/bin/env python3
"""Render the README benchmark SVG from a run's summary.json.

  python3 chart.py runs/<stamp> ../../assets/benchmark.svg

Ponytail-style grouped bars: every metric (lines of code, output tokens, cost, wall time)
as a percent of the bare baseline, four arms per group. Lower is leaner / cheaper / faster;
the dashed line is the baseline at 100%. Below it, the safety tier (higher is safer) proves
"leaner" never dropped a guard. Plotted straight from the run, nothing typed by hand; no
dependencies, the SVG is emitted by hand so the repo stays dependency-free.
"""
import json, sys
from pathlib import Path

# arm -> (key, color, label). Display order is fixed; only arms present in the run are drawn.
ARM_STYLE = [
    ("baseline",  "#b9b2a6", "baseline"),
    ("caveman",   "#d98b3f", "caveman"),
    ("ponytail",  "#5ca85c", "ponytail"),
    ("capybaraa", "#7c5cbf", "capybaraa"),
]
INK, MUTE, GRID, BG = "#2f2a22", "#777", "#e5e0d6", "#fbfaf7"

# clear build tasks with real room to differ (the % panel); only those present are used.
BUILD_TASKS = ["feat-rating", "feat-export", "feat-palette"]
SAFETY_TASKS = ["safe-path", "safe-email"]
METRICS = [
    ("src_loc_median",  "LOC",          lambda v: f"{v:g}"),
    ("out_tokens_mean", "tokens",       lambda v: f"{v/1000:.0f}k" if v >= 1000 else f"{v:g}"),
    ("cost_mean",       "cost",         lambda v: f"${v:.2f}"),
    ("time_s_mean",     "time",         lambda v: f"{v:.0f}s"),
]


def load(run_dir):
    return {(r["task"], r["arm"]): r for r in json.loads((Path(run_dir) / "summary.json").read_text())}


def render(run_dir, out_path):
    summary = load(run_dir)
    arms = [a for a, _, _ in ARM_STYLE if (a == "baseline") or any((t, a) in summary for t in BUILD_TASKS)]
    if "baseline" not in arms:
        sys.exit("no baseline rows in summary.json; cannot plot percent-of-baseline")
    color = {a: c for a, c, _ in ARM_STYLE}
    label = {a: l for a, _, l in ARM_STYLE}

    # build tasks present for every arm; sum (not average the per-task %) weights by task size.
    tasks = [t for t in BUILD_TASKS if all((t, a) in summary for a in arms)]
    n = summary[(tasks[0], "baseline")]["n"] if tasks else 0
    ratios, base_abs = {}, {}
    for key, _, _ in METRICS:
        base = sum(summary[(t, "baseline")][key] for t in tasks) or 1
        base_abs[key] = base
        ratios[key] = {a: sum(summary[(t, a)][key] for t in tasks) / base for a in arms}

    # safety tier: mean safe_rate over the safety tasks present for every arm.
    safe_tasks = [t for t in SAFETY_TASKS if all((t, a) in summary for a in arms)]
    safe = {a: sum(summary[(t, a)]["safe_rate"] for t in safe_tasks) / len(safe_tasks)
            for a in arms} if safe_tasks else {}

    # geometry
    W, padL, padR, padTop = 760, 64, 24, 92
    plotW, plotH = W - padL - padR, 300
    axis_max = 1.20                                   # headroom for arms a touch above baseline
    baseY = padTop + plotH
    ngrp, nbar = len(METRICS), len(arms)
    grpW = plotW / ngrp
    barGap, edge = 5, grpW * 0.12
    barW = (grpW - 2 * edge - (nbar - 1) * barGap) / nbar
    H = baseY + 132 + (24 if safe else 0)
    y_of = lambda pct: baseY - plotH * min(pct, axis_max) / axis_max

    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
         f'font-family="ui-sans-serif,system-ui,sans-serif"><rect width="{W}" height="{H}" fill="{BG}"/>']

    # title + legend
    s.append(f'<text x="{padL}" y="26" font-size="15" font-weight="700" fill="{INK}">'
             f'Every metric vs the no-skill baseline (Claude Code, Haiku 4.5, {len(tasks)} build tasks)</text>')
    lx = padL
    for a in arms:
        s.append(f'<rect x="{lx}" y="40" width="12" height="12" rx="2" fill="{color[a]}"/>'
                 f'<text x="{lx+17}" y="50" font-size="12" fill="#555">{label[a]}</text>')
        lx += 24 + 7.4 * len(label[a]) + 16

    # y gridlines + labels (0/25/50/75/100%)
    for pct in (0.0, 0.25, 0.5, 0.75, 1.0):
        gy = y_of(pct)
        dash = ' stroke-dasharray="3 3"' if pct == 1.0 else ''
        s.append(f'<line x1="{padL}" y1="{gy:.1f}" x2="{W-padR}" y2="{gy:.1f}" stroke="{GRID}" stroke-width="1"{dash}/>')
        s.append(f'<text x="{padL-8}" y="{gy+3:.1f}" font-size="10.5" text-anchor="end" fill="{MUTE}">{round(pct*100)}%</text>')
    s.append(f'<text x="14" y="{padTop+plotH/2:.0f}" font-size="10.5" fill="{MUTE}" '
             f'transform="rotate(-90 14 {padTop+plotH/2:.0f})" text-anchor="middle">% of baseline (lower is leaner)</text>')

    # grouped bars
    for gi, (key, mlabel, fmt) in enumerate(METRICS):
        gx = padL + gi * grpW + edge
        for bi, a in enumerate(arms):
            r = ratios[key][a]
            x = gx + bi * (barW + barGap)
            top = y_of(r)
            s.append(f'<rect x="{x:.1f}" y="{top:.1f}" width="{barW:.1f}" height="{baseY-top:.1f}" fill="{color[a]}"/>')
            s.append(f'<text x="{x+barW/2:.1f}" y="{top-4:.1f}" font-size="10" font-weight="600" '
                     f'text-anchor="middle" fill="{color[a]}">{round(r*100)}%</text>')
        # metric name + base value under the group
        cx = padL + gi * grpW + grpW / 2
        s.append(f'<text x="{cx:.1f}" y="{baseY+18:.1f}" font-size="12" font-weight="600" text-anchor="middle" fill="{INK}">{mlabel}</text>')
        s.append(f'<text x="{cx:.1f}" y="{baseY+33:.1f}" font-size="10" text-anchor="middle" fill="{MUTE}">base {fmt(base_abs[key])}</text>')

    # caption
    cap_y = baseY + 60
    s.append(f'<text x="{padL}" y="{cap_y}" font-size="10.5" fill="{MUTE}">'
             f"Each bar = that arm's mean as a % of the no-skill baseline (the dashed 100% line). "
             f"Lower is leaner / cheaper / faster. n={n} per cell.</text>")

    # safety tier
    if safe:
        sy = cap_y + 28
        s.append(f'<line x1="{padL}" y1="{sy-14:.1f}" x2="{W-padR}" y2="{sy-14:.1f}" stroke="{GRID}" stroke-width="1"/>')
        s.append(f'<text x="{padL}" y="{sy}" font-size="10.5" fill="{MUTE}">'
                 f'Safety, separate {len(safe_tasks)}-task adversarial tier (path traversal, email injection). Higher is safer:</text>')
        lx = padL
        for a in arms:
            txt = f'{label[a]} {round(safe[a]*100)}%'
            s.append(f'<text x="{lx}" y="{sy+18:.1f}" font-size="11.5" font-weight="600" fill="{color[a] if color[a]!="#b9b2a6" else "#555"}">{txt}</text>')
            lx += 7.6 * len(txt) + 26

    s.append('</svg>')
    Path(out_path).write_text("\n".join(s), encoding="utf-8")
    print(f"wrote {out_path}  (arms: {', '.join(arms)}; build tasks: {', '.join(tasks)}; safety: {', '.join(safe_tasks) or 'none'})")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("usage: python3 chart.py runs/<stamp> ../../assets/benchmark.svg")
    render(sys.argv[1], sys.argv[2])
