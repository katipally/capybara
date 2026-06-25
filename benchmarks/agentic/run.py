#!/usr/bin/env python3
"""Agentic benchmark for capybaraa: real headless Claude Code sessions, scored per pillar.

Each cell is one (task x arm x model) run inside an isolated temp workspace seeded with a
starter repo. The arm is the only thing that changes between cells, so any difference is the
plugin's effect, not the model being chatty.

  python3 run.py --selftest
      Validate every deterministic instrument offline (good ref passes, bad ref is caught).
      No API, no spend. Run this first, always.

  python3 run.py --all --arms baseline,capybaraa,concise --models haiku --runs 3
      Live run (spends API). Workspaces kept under runs/<stamp>/ for inspection.

  python3 run.py --rescore runs/<stamp>
      Recompute metrics from kept workspaces. No API.

Isolation (the lesson ponytail learned the hard way): capybaraa is a SessionStart-hook
plugin. To test exactly one arm we (1) exclude the user's global plugins with
--setting-sources project,local, (2) load capybaraa for its arm only via --plugin-dir, and
(3) give every cell its OWN CLAUDE_CONFIG_DIR so a stale "off" flag in the real ~/.claude
can't silently neuter the treatment. The capybaraa arm runs at level=high.
"""
import argparse, concurrent.futures, datetime, json, os, re, shutil, statistics, subprocess, sys, tempfile
from collections import defaultdict
from pathlib import Path

from tasks import TASKS

ROOT = Path(__file__).resolve().parents[2]          # the capybaraa plugin repo (its own plugin dir)
RUNS_DIR = Path(__file__).resolve().parent / "runs"

ARMS = ("baseline", "capybaraa", "concise")
MODELS = {"haiku": "claude-haiku-4-5-20251001", "sonnet": "claude-sonnet-4-6", "opus": "claude-opus-4-8"}
CONCISE_PROMPT = "Be concise. Build the minimal thing that works and stop."

CELL_TIMEOUT = 300
CODE_EXT = {".py", ".js", ".ts", ".jsx", ".tsx", ".html", ".css", ".go", ".rs", ".java", ".rb"}
_RAN_CHECK_RE = re.compile(r"\b(pytest|python\s+-m\s+pytest|unittest|npm\s+(run\s+)?test|jest|go\s+test|vitest)\b")

# Written code, no live servers. Tests are allowed where the task needs the done-gate.
NO_RUN = ("Write the implementation and stop. Do not start a dev server, install dependencies, "
          "run a database, or open a browser. Only the code you leave behind is measured.")
NO_RUN_TESTS_OK = ("Make the change and verify it the way you normally would. Do not start a dev "
                   "server, install dependencies, or open a browser. Running the test suite is fine.")


def _plugin_dir():
    return os.environ.get("CAPYBARAA_PLUGIN_DIR") or str(ROOT)


def _flag_path():
    base = os.environ.get("CLAUDE_CONFIG_DIR") or str(Path.home() / ".claude")
    return Path(base) / ".capybaraa-active"


def _git(workdir, *args):
    return subprocess.run([shutil.which("git") or "git", *args], cwd=str(workdir),
                          capture_output=True, text=True)


def _snapshot(workdir):
    """Commit the seeded repo so we can diff exactly what the agent adds."""
    _git(workdir, "init", "-q")
    _git(workdir, "add", "-A")
    _git(workdir, "-c", "user.email=bench@local", "-c", "user.name=bench",
         "commit", "-q", "-m", "base", "--no-verify")


def _diff_stats(workdir: Path):
    """Added lines + touched files of code-ext files vs the seeded base. Matches the '+N' a PR shows,
    so editing a seeded file counts, not just brand-new files. Underscore/dot scratch files excluded."""
    _git(workdir, "add", "-A")
    out = _git(workdir, "diff", "--cached", "--numstat", "HEAD").stdout
    loc = files = 0
    for line in out.splitlines():
        parts = line.split("\t")
        if len(parts) != 3:
            continue
        added, _deleted, path = parts
        if added == "-":                                  # binary
            continue
        name = Path(path).name
        if Path(path).suffix not in CODE_EXT or name.startswith((".", "_")) or "node_modules" in path:
            continue
        loc += int(added)
        files += 1
    return {"src_loc": loc, "src_files": files}


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
    if arm == "capybaraa":
        cmd += ["--plugin-dir", _plugin_dir()]
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

    # Real ~/.claude (auth lives there); isolation is the cwd + --setting-sources + --plugin-dir.
    # The harness pins the level flag to high for the run (see main), so the capybaraa arm
    # activates; baseline/concise never load the plugin so the flag is inert for them.
    env = dict(os.environ)
    if arm == "capybaraa":
        env["CAPYBARAA_DEFAULT_LEVEL"] = "high"

    append = NO_RUN_TESTS_OK if task.get("allow_bash") else NO_RUN
    if arm == "concise":
        append = CONCISE_PROMPT + "\n\n" + append

    cmd = _build_cmd(task, arm, model, append)
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
    # activation: the harness pinned the flag to high; capy arm should read it, others ignore it.
    flag = _flag_path()
    lvl = flag.read_text(encoding="utf-8").strip() if flag.exists() else ""
    (workdir / "_activated.txt").write_text(lvl if arm == "capybaraa" else "", encoding="utf-8")
    return score_workspace(task_id, arm, model, workdir)


def score_workspace(task_id, arm, model, workdir: Path):
    task = TASKS[task_id]
    _, meta, _ = _parse_stream(workdir / "_claude.jsonl")
    stats = _diff_stats(workdir)
    base = {"task": task_id, "arm": arm, "model": model,
            "src_files": stats["src_files"], "src_loc": stats["src_loc"],
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
               "cost_mean": mean("cost"),
               "time_s_mean": round(mean("duration_ms") / 1000, 1) if mean("duration_ms") else None}
        if TASKS[t].get("judge_only"):
            row.update({"premature_files_median": med("premature_files"), "asked_proxy_rate": rate("asked_proxy")})
        else:
            row.update({"correct_rate": rate("correct"), "safe_rate": rate("safe")})
            for extra in ("reuse", "native", "hygiene", "ran_check"):
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
            else:
                bits += [f"correct%={r.get('correct_rate')}", f"safe%={r.get('safe_rate')}"]
                for extra in ("reuse_rate", "native_rate", "hygiene_rate", "ran_check_rate"):
                    if extra in r:
                        bits.append(f"{extra.replace('_rate','')}%={r[extra]}")
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
    ap.add_argument("--arms", default=",".join(ARMS))
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
    models = [m.strip() for m in args.models.split(",")]
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    out_dir = RUNS_DIR / stamp
    out_dir.mkdir(parents=True, exist_ok=True)

    cells = [(t, a, m, r) for t in task_ids for m in models for a in arms for r in range(args.runs)]
    total, results, done = len(cells), [], 0
    print(f"running {total} cells, {args.workers} at a time", flush=True)

    # Pin the level flag to high so the capybaraa arm activates regardless of any stale state;
    # restore the user's original setting when we're done. baseline/concise never load the plugin.
    flag = _flag_path()
    orig_flag = flag.read_text(encoding="utf-8") if flag.exists() else None
    if "capybaraa" in arms:
        flag.parent.mkdir(parents=True, exist_ok=True)
        flag.write_text("high\n", encoding="utf-8")

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
        if "capybaraa" in arms:                       # restore the user's original level
            if orig_flag is None:
                flag.unlink(missing_ok=True)
            else:
                flag.write_text(orig_flag, encoding="utf-8")

    rows = aggregate(results)
    (out_dir / "summary.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print_table(rows)
    print(f"\nwrote {out_dir}/results.json + summary.json ({len(results)} cells)")


if __name__ == "__main__":
    main()
