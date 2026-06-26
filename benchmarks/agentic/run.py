#!/usr/bin/env python3
"""Agentic benchmark for capybaraa: real headless Claude Code sessions, scored per pillar.

Each cell is one (task x arm x model) run inside an isolated temp workspace seeded with a
starter repo. The arm is the only thing that changes between cells, so any difference is the
plugin's effect, not the model being chatty.

  python3 run.py --selftest
      Validate every deterministic instrument offline (good ref passes, bad ref is caught).
      No API, no spend. Run this first, always.

  python3 run.py --all --arms baseline,capybaraa --models haiku --runs 3
      Live run (spends API). Workspaces kept under runs/<stamp>/ for inspection.

  python3 run.py --rescore runs/<stamp>
      Recompute metrics from kept workspaces. No API.

Isolation: capybaraa is a SessionStart-hook plugin. To test exactly one arm we (1) exclude
the user's global plugins with --setting-sources project,local, (2) load capybaraa for its
arm only via --plugin-dir, and (3) pin its activation flag for the run so a stale "off" in
the real ~/.claude can't silently neuter the treatment. The baseline arm loads no plugin,
so any difference between the two arms is capybaraa's effect, not the model being chatty.
"""
import argparse, concurrent.futures, datetime, json, os, re, shutil, statistics, subprocess, sys, tempfile
from collections import defaultdict
from pathlib import Path

from tasks import TASKS

ROOT = Path(__file__).resolve().parents[2]          # the capybaraa plugin repo (its own plugin dir)
RUNS_DIR = Path(__file__).resolve().parent / "runs"

MODELS = {"haiku": "claude-haiku-4-5-20251001", "sonnet": "claude-sonnet-4-6", "opus": "claude-opus-4-8"}

# Arms. Three kinds:
#   bare   - the unaided agent (the fair baseline / "regular"), the only thing capybaraa is
#            compared against
#   plugin - capybaraa itself, loaded via --plugin-dir; `src` resolves the dir, `flag`/`level`
#            pin its activation flag for the run (restored after)
#   prompt - a generic system-prompt instruction via --append-system-prompt (no plugin); these
#            are optional reference points, not part of the headline baseline-vs-capybaraa read
ARMS = {
    "baseline":       {"kind": "bare"},
    "regular":        {"kind": "bare"},                                   # alias for baseline
    "capybaraa":      {"kind": "plugin", "src": "capybaraa", "flag": ".capybaraa-active", "level": "on"},
    "yagni":          {"kind": "prompt", "text": "Follow YAGNI principles."},
    "yagni-oneliner": {"kind": "prompt", "text": "Follow YAGNI principles, and prefer one-liner solutions."},
    "concise":        {"kind": "prompt", "text": "Be concise. Build the minimal thing that works and stop."},
}
DEFAULT_ARMS = ("baseline", "capybaraa")

CELL_TIMEOUT = 300
CODE_EXT = {".py", ".js", ".ts", ".jsx", ".tsx", ".html", ".css", ".go", ".rs", ".java", ".rb"}
_RAN_CHECK_RE = re.compile(r"\b(pytest|python\s+-m\s+pytest|unittest|npm\s+(run\s+)?test|jest|go\s+test|vitest)\b")

# Written code, no live servers. Tests are allowed where the task needs the done-gate.
NO_RUN = ("Write the implementation and stop. Do not start a dev server, install dependencies, "
          "run a database, or open a browser. Only the code you leave behind is measured.")
NO_RUN_TESTS_OK = ("Make the change and verify it the way you normally would. Do not start a dev "
                   "server, install dependencies, or open a browser. Running the test suite is fine.")
# CLARIFY (judge_only) measures whether the agent asks before coding, so it must NOT be told
# "only the code is measured" (that punishes asking). Neutral: respond however you would, just
# don't run anything live.
NO_RUN_NEUTRAL = ("Respond in a single message as you normally would. Do not start a dev server, "
                  "install dependencies, run a database, or open a browser.")


def _resolve_plugin(src):
    """capybaraa -> the dev repo (override with CAPYBARAA_PLUGIN_DIR). capybaraa is the only
    plugin arm; returns None only if the override points nowhere."""
    env = os.environ.get(f"{src.upper()}_PLUGIN_DIR")
    if env:
        return env
    if src == "capybaraa":
        return str(ROOT)
    return None


def _arm_append(arm):
    """The --append text for a prompt arm (None for bare/plugin arms)."""
    spec = ARMS[arm]
    if spec["kind"] != "prompt":
        return None
    return spec["text"]


def _flag_path(name=".capybaraa-active"):
    base = os.environ.get("CLAUDE_CONFIG_DIR") or str(Path.home() / ".claude")
    return Path(base) / name


def _git(workdir, *args):
    return subprocess.run([shutil.which("git") or "git", *args], cwd=str(workdir),
                          capture_output=True, text=True)


def _snapshot(workdir):
    """Commit the seeded repo so we can diff exactly what the agent adds."""
    _git(workdir, "init", "-q")
    _git(workdir, "add", "-A")
    _git(workdir, "-c", "user.email=bench@local", "-c", "user.name=bench",
         "commit", "-q", "-m", "base", "--no-verify")


def _is_test(path: str):
    """A produced file is a test if named like one or living in a tests/ dir. Writing a test is
    the COMPLETE pillar's discipline, a POSITIVE signal, so it is never counted as source bloat."""
    p = Path(path)
    name = p.name.lower()
    if any(part.lower() in ("test", "tests", "__tests__") for part in p.parts[:-1]):
        return True
    # any file whose name is or contains a test/spec token at a word boundary:
    # test.js, test-widget.js, run-test.js, foo.test.ts, foo_test.py, spec.js (not "latest.js")
    return bool(re.search(r"(^|[._-])(test|spec)([._-]|$)", name))


def _diff_stats(workdir: Path):
    """Added lines + touched files of code-ext files vs the seeded base. Matches the '+N' a PR shows,
    so editing a seeded file counts, not just brand-new files. Tests are tracked SEPARATELY (never
    as source bloat); underscore/dot scratch files excluded."""
    _git(workdir, "add", "-A")
    out = _git(workdir, "diff", "--cached", "--numstat", "HEAD").stdout
    loc = files = test_loc = test_files = 0
    for line in out.splitlines():
        parts = line.split("\t")
        if len(parts) != 3:
            continue
        added, _deleted, path = parts
        if added == "-":                                  # binary
            continue
        name = Path(path).name
        if Path(path).suffix not in CODE_EXT or name.startswith((".", "_")):
            continue
        # agent scratch and deps are not delivered code: subagent worktrees live under .claude/
        if any(seg in path.split("/") for seg in ("node_modules", ".claude")) or ".claude/" in path:
            continue
        if _is_test(path):
            test_loc += int(added); test_files += 1
        else:
            loc += int(added); files += 1
    return {"src_loc": loc, "src_files": files, "test_loc": test_loc, "test_files": test_files}


# ─────────────────────────── headless cell ───────────────────────────
def _build_cmd(task, arm, model, append):
    claude = shutil.which("claude")
    if not claude:
        sys.exit("claude CLI not found on PATH")
    cmd = [claude, "-p", task["prompt"], "--model", MODELS[model],
           "--permission-mode", "bypassPermissions",
           "--output-format", "stream-json", "--verbose",
           "--setting-sources", "project,local", "--strict-mcp-config"]
    if not task.get("allow_bash"):
        cmd += ["--disallowedTools", "Bash"]
    if ARMS[arm]["kind"] == "plugin":
        pdir = _resolve_plugin(ARMS[arm]["src"])
        if not pdir:
            raise RuntimeError(f"{arm} plugin not installed (set {ARMS[arm]['src'].upper()}_PLUGIN_DIR)")
        cmd += ["--plugin-dir", pdir]
    cmd += ["--append-system-prompt", append]
    return cmd


def _parse_stream(path: Path):
    """Return (result_text, meta, bash_cmds) from a stream-json transcript."""
    result_text, meta, bash = "", {}, []
    try:
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except Exception:
        return result_text, meta, bash
    for ln in lines:
        ln = ln.strip()
        if not ln:
            continue
        try:
            ev = json.loads(ln)
        except Exception:
            continue
        if ev.get("type") in ("assistant", "user"):
            for block in (ev.get("message", {}) or {}).get("content", []) or []:
                if isinstance(block, dict) and block.get("type") == "tool_use" and block.get("name") == "Bash":
                    bash.append((block.get("input", {}) or {}).get("command", ""))
        elif ev.get("type") == "result":
            result_text = ev.get("result", "") or ""
            u = ev.get("usage") or {}
            meta = {"cost": ev.get("total_cost_usd"), "duration_ms": ev.get("duration_ms"),
                    "turns": ev.get("num_turns"),
                    "out_tokens": u.get("output_tokens"), "in_tokens": u.get("input_tokens"),
                    "cache_tokens": (u.get("cache_read_input_tokens") or 0) + (u.get("cache_creation_input_tokens") or 0)}
    return result_text, meta, bash


def run_cell(task_id, arm, model, workdir: Path):
    task = TASKS[task_id]
    seeded = set()
    for rel, content in task.get("seed", {}).items():
        p = workdir / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        seeded.add(rel.replace("\\", "/"))
    _snapshot(workdir)                                # base commit -> diff the agent's additions

    # Real ~/.claude (auth lives there); isolation is the cwd + --setting-sources + one --plugin-dir.
    # main() pins each plugin arm's level flag for the run, so plugin arms activate; bare/prompt
    # arms load no plugin so the flags are inert for them.
    spec = ARMS[arm]
    env = dict(os.environ)
    if spec["kind"] == "plugin":
        env[f"{spec['src'].upper()}_DEFAULT_LEVEL"] = spec["level"]   # belt-and-suspenders for activation

    if task.get("judge_only"):
        append = NO_RUN_NEUTRAL
    elif task.get("allow_bash"):
        append = NO_RUN_TESTS_OK
    else:
        append = NO_RUN
    arm_text = _arm_append(arm)
    if arm_text:
        append = arm_text + "\n\n" + append

    try:
        cmd = _build_cmd(task, arm, model, append)
    except RuntimeError as e:                              # plugin not installed -> skip this cell cleanly
        (workdir / "_claude.jsonl").write_text(json.dumps({"type": "result", "result": "", "error": str(e)}), encoding="utf-8")
        (workdir / "_activated.txt").write_text("", encoding="utf-8")
        (workdir / "_ran_check.txt").write_text("0", encoding="utf-8")
        return {"task": task_id, "arm": arm, "model": model, "error": str(e), "src_loc": 0, "src_files": 0}
    out_path, err_path = workdir / "_claude.jsonl", workdir / "_claude.stderr.txt"
    try:
        with open(out_path, "wb") as so, open(err_path, "wb") as se:
            proc = subprocess.Popen(cmd, cwd=str(workdir), stdout=so, stderr=se, env=env)
            try:
                proc.wait(timeout=CELL_TIMEOUT)
            except subprocess.TimeoutExpired:
                proc.kill()
                se.write(f"\n[KILLED after {CELL_TIMEOUT}s]".encode())
    except Exception as e:
        out_path.write_text(json.dumps({"type": "result", "result": "", "error": str(e)[:200]}), encoding="utf-8")

    result_text, _, bash = _parse_stream(out_path)
    (workdir / "_result.txt").write_text(result_text, encoding="utf-8")
    ran = 1 if any(_RAN_CHECK_RE.search(c or "") for c in bash) else 0
    (workdir / "_ran_check.txt").write_text(str(ran), encoding="utf-8")
    # activation: read this plugin arm's pinned flag back (proof the right hook fired); bare/prompt -> empty
    if spec["kind"] == "plugin":
        flag = _flag_path(spec["flag"])
        lvl = flag.read_text(encoding="utf-8").strip() if flag.exists() else ""
    else:
        lvl = ""
    (workdir / "_activated.txt").write_text(lvl, encoding="utf-8")
    return score_workspace(task_id, arm, model, workdir)


def score_workspace(task_id, arm, model, workdir: Path):
    task = TASKS[task_id]
    _, meta, _ = _parse_stream(workdir / "_claude.jsonl")
    stats = _diff_stats(workdir)
    base = {"task": task_id, "arm": arm, "model": model,
            "src_files": stats["src_files"], "src_loc": stats["src_loc"],
            "test_files": stats["test_files"], "test_loc": stats["test_loc"],
            "activated": (workdir / "_activated.txt").read_text(encoding="utf-8").strip()
                         if (workdir / "_activated.txt").exists() else "",
            **meta}
    if task.get("judge_only"):
        # CLARIFY: no deterministic answer. premature_files = code written before asking.
        # asked = does the result text contain a question? (cheap proxy; judge.py scores quality)
        rt = (workdir / "_result.txt").read_text(encoding="utf-8") if (workdir / "_result.txt").exists() else ""
        base.update({"premature_files": stats["src_files"], "asked_proxy": 1 if "?" in rt else 0,
                     "reason": "judge_only"})
        return base
    if task.get("open"):
        # over-build trap: no gate, LOC is the over-engineering signal; completeness via judge.py.
        base.update({"wrote_code": 1 if stats["src_loc"] > 0 else 0, "reason": "open/LOC"})
        return base
    sc = task["score"](workdir)
    base.update(sc)
    return base


# ─────────────────────────── offline selftest ───────────────────────────
def selftest():
    fails = 0
    for tid, task in TASKS.items():
        if task.get("judge_only"):
            print(f"..  {tid:18} judge-only (no deterministic gate; validate with judge.py --selftest)")
            continue
        if task.get("open"):
            print(f"..  {tid:18} open LOC tier (completeness via judge.py --complete-run)")
            continue
        axis = task.get("axis", "correct")
        for kind in ("good", "bad"):
            with tempfile.TemporaryDirectory() as d:
                d = Path(d)
                for rel, content in task.get("seed", {}).items():
                    (d / rel).parent.mkdir(parents=True, exist_ok=True)
                    (d / rel).write_text(content, encoding="utf-8")
                (d / task["file"]).parent.mkdir(parents=True, exist_ok=True)
                (d / task["file"]).write_text(task[kind], encoding="utf-8")
                if task.get("allow_bash"):           # COMPLETE: no agent ran, so fake the flag
                    (d / "_ran_check.txt").write_text("0", encoding="utf-8")
                r = task["score"](d)
            ok = (r["correct"] == 1 and r["safe"] == 1) if kind == "good" else (r.get(axis, r["correct"]) == 0)
            print(f"{'ok ' if ok else 'XX '} {tid:18} {kind:4} "
                  f"correct={r['correct']} safe={r['safe']} {axis}={r.get(axis,'-')}  {r['reason']}")
            fails += 0 if ok else 1
    print(f"\nselftest: {'all instruments valid' if not fails else str(fails) + ' BROKEN'}")
    return fails


# ─────────────────────────── aggregate + report ───────────────────────────
def aggregate(results):
    groups = defaultdict(list)
    for r in results:
        groups[(r["task"], r["arm"], r["model"])].append(r)
    rows = []
    for (t, a, m), cells in sorted(groups.items()):
        n = len(cells)
        def rate(key): return round(sum(c.get(key, 0) for c in cells) / n, 3)
        def med(key):
            vals = [c[key] for c in cells if c.get(key) is not None]
            return statistics.median(vals) if vals else None
        def mean(key):
            vals = [c[key] for c in cells if c.get(key) is not None]
            return round(statistics.mean(vals), 4) if vals else None
        row = {"task": t, "arm": a, "model": m, "n": n,
               "pillar": TASKS[t]["pillar"],
               "src_loc_median": med("src_loc"), "src_files_median": med("src_files"),
               "wrote_tests_rate": round(sum(1 for c in cells if c.get("test_files", 0) > 0) / n, 3),
               "test_loc_median": med("test_loc"),
               "cost_mean": mean("cost"),
               "time_s_mean": round(mean("duration_ms") / 1000, 1) if mean("duration_ms") else None}
        if TASKS[t].get("judge_only"):
            row.update({"premature_files_median": med("premature_files"), "asked_proxy_rate": rate("asked_proxy")})
        elif TASKS[t].get("open"):
            row.update({"total_loc_max": max((c.get("src_loc", 0) for c in cells), default=0),
                        "wrote_code_rate": rate("wrote_code")})
        else:
            row.update({"correct_rate": rate("correct"), "safe_rate": rate("safe")})
            for extra in ("reuse", "native", "optimal", "economy", "sync", "hygiene", "ran_check"):
                if any(extra in c for c in cells):
                    row[extra + "_rate"] = rate(extra)
        rows.append(row)
    return rows


def print_table(rows):
    by = defaultdict(list)
    for r in rows:
        by[(r["pillar"], r["task"], r["model"])].append(r)
    for (pillar, task, model), rs in sorted(by.items()):
        print(f"\n=== [{pillar}] {task}  ({model}, n={rs[0]['n']}) ===")
        for r in sorted(rs, key=lambda x: x["arm"]):
            cost = ("$" + format(r["cost_mean"], ".4f")) if r.get("cost_mean") is not None else "-"
            bits = [f"{r['arm']:10}", f"LOC={r.get('src_loc_median')}", f"files={r.get('src_files_median')}"]
            if TASKS[task].get("judge_only"):
                bits += [f"premature_files={r.get('premature_files_median')}", f"asked%={r.get('asked_proxy_rate')}"]
            elif TASKS[task].get("open"):
                bits += [f"LOCmax={r.get('total_loc_max')}", f"built%={r.get('wrote_code_rate')}"]
            else:
                bits += [f"correct%={r.get('correct_rate')}", f"safe%={r.get('safe_rate')}"]
                for extra in ("reuse_rate", "native_rate", "optimal_rate", "economy_rate",
                              "sync_rate", "hygiene_rate", "ran_check_rate"):
                    if extra in r:
                        bits.append(f"{extra.replace('_rate','')}%={r[extra]}")
            bits.append(f"tests%={r.get('wrote_tests_rate')}")
            bits += [f"{cost}", f"{r.get('time_s_mean')}s"]
            print("  " + "  ".join(str(b) for b in bits))


def rescore(run_dir):
    run_dir = Path(run_dir)
    if not run_dir.exists():
        run_dir = RUNS_DIR / run_dir.name
    results = []
    for ws in sorted(p for p in run_dir.iterdir() if p.is_dir()):
        parts = ws.name.split("__")
        if len(parts) != 4 or parts[0] not in TASKS:
            continue
        tid, arm, model, _ = parts
        results.append(score_workspace(tid, arm, model, ws))
    rows = aggregate(results)
    (run_dir / "summary.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print_table(rows)
    print(f"\nrescored {len(results)} cells from {run_dir}")


def _claude_version():
    try:
        return subprocess.run([shutil.which("claude"), "--version"], capture_output=True, text=True).stdout.strip()
    except Exception:
        return "unknown"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--rescore")
    ap.add_argument("--task")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--arms", default=",".join(DEFAULT_ARMS),
                    help="comma list from: " + ", ".join(ARMS))
    ap.add_argument("--models", default="haiku")
    ap.add_argument("--runs", type=int, default=1)
    ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args()

    if args.selftest:
        sys.exit(1 if selftest() else 0)
    if args.rescore:
        return rescore(args.rescore)
    if selftest():
        sys.exit("instruments broken; refusing to spend on the API")

    task_ids = (list(TASKS) if args.all
                else ([t.strip() for t in args.task.split(",")] if args.task else []))
    if not task_ids:
        sys.exit("give --task <id[,id...]>, --all, or --rescore <dir>")
    arms = [a.strip() for a in args.arms.split(",")]
    unknown = [a for a in arms if a not in ARMS]
    if unknown:
        sys.exit(f"unknown arm(s): {unknown}. choose from: {', '.join(ARMS)}")
    for a in arms:                                         # fail early if a plugin arm isn't installed
        if ARMS[a]["kind"] == "plugin" and not _resolve_plugin(ARMS[a]["src"]):
            sys.exit(f"arm '{a}' needs the {ARMS[a]['src']} plugin installed (or set {ARMS[a]['src'].upper()}_PLUGIN_DIR)")
    models = [m.strip() for m in args.models.split(",")]
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    out_dir = RUNS_DIR / stamp
    out_dir.mkdir(parents=True, exist_ok=True)

    cells = [(t, a, m, r) for t in task_ids for m in models for a in arms for r in range(args.runs)]
    total, results, done = len(cells), [], 0
    print(f"running {total} cells, {args.workers} at a time", flush=True)

    # Pin each plugin arm's level flag so it activates regardless of any stale state; restore the
    # user's originals when done. bare/prompt arms load no plugin, so the flags are inert for them.
    pinned = []                                            # (flag_path, original_text_or_None)
    for a in arms:
        spec = ARMS[a]
        if spec["kind"] != "plugin":
            continue
        fp = _flag_path(spec["flag"])
        pinned.append((fp, fp.read_text(encoding="utf-8") if fp.exists() else None))
        fp.parent.mkdir(parents=True, exist_ok=True)
        fp.write_text(spec["level"] + "\n", encoding="utf-8")

    def _one(spec):
        tid, arm, model, r = spec
        ws = out_dir / f"{tid}__{arm}__{model}__{r}"
        ws.mkdir(parents=True, exist_ok=True)
        return run_cell(tid, arm, model, ws)

    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as ex:
            futs = {ex.submit(_one, s): s for s in cells}
            for fut in concurrent.futures.as_completed(futs):
                tid, arm, model, r = futs[fut]
                try:
                    res = fut.result()
                except Exception as e:
                    res = {"task": tid, "arm": arm, "model": model, "error": str(e)[:200]}
                results.append(res)
                done += 1
                print(f"  [{done}/{total}] {tid}/{arm}/{model}#{r}  LOC={res.get('src_loc')} "
                      f"correct={res.get('correct')} act={res.get('activated')!r} "
                      f"cost=${res.get('cost')} {round((res.get('duration_ms') or 0)/1000,1)}s", flush=True)
                (out_dir / "results.json").write_text(json.dumps(
                    {"date": stamp, "claude": _claude_version(),
                     "models": {m: MODELS[m] for m in models}, "results": results}, indent=2), encoding="utf-8")
    finally:
        for fp, orig in pinned:                       # restore each plugin's original level
            if orig is None:
                fp.unlink(missing_ok=True)
            else:
                fp.write_text(orig, encoding="utf-8")

    rows = aggregate(results)
    (out_dir / "summary.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print_table(rows)
    print(f"\nwrote {out_dir}/results.json + summary.json ({len(results)} cells)")


if __name__ == "__main__":
    main()
