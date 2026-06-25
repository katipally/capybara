#!/usr/bin/env python3
"""CLARIFY judge: did the agent ask the questions a senior dev must ask before coding?

The CLARIFY pillar has no deterministic answer, so it gets an auditable LLM judge: a fixed
model, a published rubric, and every verdict must name which required clarifications were
asked and which were missed. The judge runs through the `claude` CLI with NO plugins loaded
(--setting-sources project + a clean config dir) so capybaraa cannot grade itself.

  python3 judge.py --selftest-offline   # validate JSON parsing + gate logic, no API
  python3 judge.py --selftest           # validate the judge ranks 'asked' above 'assumed' (small spend)
  python3 judge.py --run runs/<stamp>   # score every clarify-* workspace, write clarify.json

Rubric (0-3): how fully did the answer clarify the ambiguous spec BEFORE writing code?
  0 = dove straight into code on its own assumptions, asked nothing that mattered
  1 = asked one shallow/generic question, still assumed the rest
  2 = asked most of the key questions, one important one missing
  3 = asked the key questions a senior dev needs, did not guess the spec
"""
import argparse, json, re, shutil, subprocess, sys
from pathlib import Path

from tasks import TASKS

JUDGE_MODEL = "claude-sonnet-4-6"

RUBRIC = (
    "Score 0-3 how fully the ANSWER clarified the ambiguous ticket BEFORE writing code.\n"
    "  0 = wrote code on its own assumptions, asked nothing that mattered\n"
    "  1 = asked one shallow or generic question, assumed the rest\n"
    "  2 = asked most of the key questions, one important one missing\n"
    "  3 = asked the key questions a senior dev needs, did not guess the spec\n"
    "Asking good questions BEFORE coding is the desired behavior; silently assuming a spec and "
    "producing code is the failure being measured.")


def _build_prompt(ticket, required, answer):
    return (
        "You are grading whether a coding assistant clarified an ambiguous ticket before coding.\n\n"
        f"TICKET: {ticket}\n\n"
        f"A senior dev cannot build this without clarifying: {required}\n\n"
        f"{RUBRIC}\n\n"
        "ANSWER UNDER TEST (verbatim):\n"
        "<<<\n" + (answer or "")[:6000] + "\n>>>\n\n"
        "Reply with ONLY a JSON object, no prose:\n"
        '{"score": <0-3>, "asked": ["..."], "missed": ["..."], "reason": "<=200 chars"}')


def _extract_json(text):
    m = re.search(r"\{.*\}", text or "", re.S)
    if not m:
        return None
    try:
        obj = json.loads(m.group(0))
        if isinstance(obj.get("score"), (int, float)) and 0 <= obj["score"] <= 3:
            return obj
    except Exception:
        return None
    return None


def _call_claude(prompt):
    """Run one judging prompt through the CLI with NO user plugins (capybaraa cannot grade
    itself) and no config-dir redirect (that would break auth). Returns parsed JSON or None."""
    claude = shutil.which("claude")
    if not claude:
        sys.exit("claude CLI not found on PATH")
    cmd = [claude, "-p", prompt, "--model", JUDGE_MODEL, "--output-format", "json",
           "--setting-sources", "project", "--strict-mcp-config",
           "--disallowedTools", "Bash,Edit,Write,Read,Glob,Grep,WebFetch,WebSearch"]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    try:
        result_text = json.loads(r.stdout).get("result", "")
    except Exception:
        result_text = r.stdout
    return _extract_json(result_text)


def _judge(ticket, required, answer):
    return _call_claude(_build_prompt(ticket, required, answer))


# ─────────────────────────── completeness judge (open LOC tier) ───────────────────────────
COMPLETE_RUBRIC = (
    "Score 0-3 how FULLY the code implements the ticket (read it alongside the LOC table: a "
    "low-LOC arm that shipped a stub is doing less, not less-bloated, and must be caught here).\n"
    "  0 = stub or placeholder, the feature does not work\n"
    "  1 = partial, core behavior missing\n"
    "  2 = mostly complete, a stated requirement missing\n"
    "  3 = fully implements what the ticket asked")


def _build_complete_prompt(ticket, code):
    return (
        "You are grading how completely a coding assistant implemented a feature ticket.\n\n"
        f"TICKET: {ticket}\n\n"
        f"{COMPLETE_RUBRIC}\n\n"
        "PRODUCED CODE (verbatim):\n<<<\n" + (code or "")[:8000] + "\n>>>\n\n"
        "Reply with ONLY a JSON object, no prose:\n"
        '{"score": <0-3>, "works": <true|false>, "missing": ["..."], "reason": "<=200 chars"}')


def _judge_complete(ticket, code):
    return _call_claude(_build_complete_prompt(ticket, code))


def _read_code(ws: Path):
    """Concatenate the produced web files of an open-task workspace for the completeness judge."""
    out = []
    for p in sorted(ws.rglob("*")):
        if p.is_file() and p.suffix in (".html", ".js", ".css") and not p.name.startswith((".", "_")) \
           and "node_modules" not in p.parts:
            try:
                out.append(f"// {p.relative_to(ws)}\n" + p.read_text(encoding="utf-8", errors="ignore"))
            except Exception:
                pass
    return "\n\n".join(out)


# full vs stub references for the open feature tasks; --selftest-complete proves full > stub.
_COMPLETE_REFS = {
    "feat-rating": {
        "full": ('<div id="rating">' + "".join(f'<span data-v="{i}">&#9733;</span>' for i in range(1, 6)) + "</div>"
                 + '<script>document.querySelectorAll("#rating span").forEach(s=>s.onclick=e=>{'
                   'const v=+e.target.dataset.v;document.querySelectorAll("#rating span").forEach('
                   '(x,i)=>x.style.color=i<v?"gold":"gray");});</script>'),
        "stub": '<div id="rating">Rating: TODO</div>',
    },
    "feat-export": {
        "full": ('<button id="exp">Export CSV</button><script>document.getElementById("exp").onclick=()=>{'
                 'const rows=[...document.querySelectorAll("#report tr")].map(r=>[...r.children]'
                 '.map(c=>c.textContent).join(",")).join("\\n");const a=document.createElement("a");'
                 'a.href="data:text/csv,"+encodeURIComponent(rows);a.download="report.csv";a.click();};</script>'),
        "stub": '<button id="exp">Export CSV</button>',
    },
    "feat-palette": {
        "full": ('<script>document.addEventListener("keydown",e=>{if((e.metaKey||e.ctrlKey)&&e.key==="k"){'
                 'e.preventDefault();const q=prompt("Go to:");const m=[...document.querySelectorAll("#nav a")]'
                 '.find(a=>a.textContent.toLowerCase().includes((q||"").toLowerCase()));'
                 'if(m)location.href=m.getAttribute("href");}});</script>'),
        "stub": "<!-- command palette: TODO -->",
    },
}


# good = asks the key questions; stub = dives in assuming. Used by --selftest.
_REFS = {
    "clarify-settings": {
        "good": ("Before I touch code, a couple of questions:\n1. Which settings/fields are we "
                 "persisting?\n2. Where should they live: localStorage, your backend API, or both?\n"
                 "3. Per-device, or synced to the user's account?"),
        "stub": ("Added settings persistence. I created a SettingsManager class and a ConfigProvider "
                 "that saves everything to localStorage as JSON.\n```js\nclass SettingsManager{...}\n```"),
    },
    "clarify-export": {
        "good": ("A few questions before building:\n1. Export to which format: CSV, PDF, Excel, JSON?\n"
                 "2. Which rows: the current filtered view, or all data?\n3. A client-side download or "
                 "a server endpoint?"),
        "stub": ("Done. Added an Export button that serializes the table to CSV and triggers a download.\n"
                 "```js\nfunction exportCsv(){...}\n```"),
    },
}


def selftest_offline():
    """Gate logic only: a higher score must beat a lower one; bad JSON is rejected. No API."""
    fails = 0
    cases = [("good>stub", {"score": 3}, {"score": 0}, True),
             ("tie rejected", {"score": 2}, {"score": 2}, False),
             ("parse junk", _extract_json("not json"), None, None)]
    for name, g, s, want in cases[:2]:
        ok = (g["score"] > s["score"]) == want
        print(f"{'ok ' if ok else 'XX '} offline {name}")
        fails += 0 if ok else 1
    ok = _extract_json("no json here") is None and _extract_json('{"score": 2, "reason": "x"}')["score"] == 2
    print(f"{'ok ' if ok else 'XX '} offline json-extract")
    fails += 0 if ok else 1
    print(f"\njudge selftest-offline: {'gate logic valid' if not fails else str(fails) + ' BROKEN'}")
    return fails


def selftest():
    if selftest_offline():
        return 1
    fails = 0
    for tid, refs in _REFS.items():
        task = TASKS[tid]
        g = _judge(task["prompt"], task["clarify_rubric"], refs["good"])
        s = _judge(task["prompt"], task["clarify_rubric"], refs["stub"])
        if not g or not s:
            print(f"XX  {tid}: judge returned no parseable score (g={g} s={s})")
            fails += 1
            continue
        ok = g["score"] > s["score"]
        print(f"{'ok ' if ok else 'XX '} {tid:18} asked={g['score']} assumed={s['score']}")
        fails += 0 if ok else 1
    print(f"\njudge selftest: {'judge trustworthy' if not fails else str(fails) + ' BROKEN'}")
    return fails


def selftest_complete():
    fails = 0
    for tid, refs in _COMPLETE_REFS.items():
        task = TASKS[tid]
        f = _judge_complete(task["prompt"], refs["full"])
        s = _judge_complete(task["prompt"], refs["stub"])
        if not f or not s:
            print(f"XX  {tid}: completeness judge no score (full={f} stub={s})")
            fails += 1
            continue
        ok = f["score"] > s["score"]
        print(f"{'ok ' if ok else 'XX '} {tid:18} full={f['score']} stub={s['score']}")
        fails += 0 if ok else 1
    print(f"\ncompleteness selftest: {'judge trustworthy' if not fails else str(fails) + ' BROKEN'}")
    return fails


def complete_run(run_dir):
    run_dir = Path(run_dir)
    if not run_dir.exists():
        run_dir = Path(__file__).resolve().parent / "runs" / run_dir.name
    out = []
    for ws in sorted(p for p in run_dir.iterdir() if p.is_dir()):
        parts = ws.name.split("__")
        if len(parts) != 4 or parts[0] not in TASKS or not TASKS[parts[0]].get("open"):
            continue
        tid, arm, model, r = parts
        v = _judge_complete(TASKS[tid]["prompt"], _read_code(ws)) or {"score": None, "reason": "no-verdict"}
        out.append({"task": tid, "arm": arm, "model": model, "run": r, **v})
        print(f"  {tid}/{arm}/{model}#{r}  complete={v.get('score')}  {v.get('reason','')[:70]}")
    (run_dir / "completeness.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    import statistics
    from collections import defaultdict
    by = defaultdict(list)
    for rec in out:
        if rec.get("score") is not None:
            by[rec["arm"]].append(rec["score"])
    print("\ncompleteness (median, higher = more fully built):")
    for arm, s in sorted(by.items()):
        print(f"  {arm:10} {statistics.median(s)}  (n={len(s)})")
    print(f"\nwrote {run_dir}/completeness.json")


def run(run_dir):
    run_dir = Path(run_dir)
    if not run_dir.exists():
        run_dir = Path(__file__).resolve().parent / "runs" / run_dir.name
    out = []
    for ws in sorted(p for p in run_dir.iterdir() if p.is_dir()):
        parts = ws.name.split("__")
        if len(parts) != 4 or parts[0] not in TASKS or not TASKS[parts[0]].get("judge_only"):
            continue
        tid, arm, model, r = parts
        answer = (ws / "_result.txt").read_text(encoding="utf-8") if (ws / "_result.txt").exists() else ""
        task = TASKS[tid]
        v = _judge(task["prompt"], task["clarify_rubric"], answer) or {"score": None, "reason": "no-verdict"}
        rec = {"task": tid, "arm": arm, "model": model, "run": r, **v}
        out.append(rec)
        print(f"  {tid}/{arm}/{model}#{r}  clarify_score={v.get('score')}  {v.get('reason','')[:80]}")
    (run_dir / "clarify.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    # arm medians
    import statistics
    from collections import defaultdict
    by = defaultdict(list)
    for rec in out:
        if rec.get("score") is not None:
            by[rec["arm"]].append(rec["score"])
    print("\nclarify score (median, higher = asked more before coding):")
    for arm, scores in sorted(by.items()):
        print(f"  {arm:10} {statistics.median(scores)}  (n={len(scores)})")
    print(f"\nwrote {run_dir}/clarify.json")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest-offline", action="store_true")
    ap.add_argument("--selftest", action="store_true", help="validate the CLARIFY judge (small spend)")
    ap.add_argument("--selftest-complete", action="store_true", help="validate the completeness judge (small spend)")
    ap.add_argument("--run", help="CLARIFY-score the judge_only tasks in a run dir")
    ap.add_argument("--complete-run", help="completeness-score the open tasks in a run dir")
    args = ap.parse_args()
    if args.selftest_offline:
        sys.exit(1 if selftest_offline() else 0)
    if args.selftest:
        sys.exit(1 if selftest() else 0)
    if args.selftest_complete:
        sys.exit(1 if selftest_complete() else 0)
    if args.run:
        return run(args.run)
    if args.complete_run:
        return complete_run(args.complete_run)
    ap.print_help()


if __name__ == "__main__":
    main()
