# Agentic benchmark

The single-shot bench (`../promptfooconfig.yaml`) measures one prompt, one completion. It
can only see lines of code, which is the one dimension capybaraa barely moves. Capybaraa's
value is behavioral: ask before coding, reuse what exists, run the check, leave the repo
clean. None of that shows up in a one-shot LOC count, which is why the difference feels
invisible.

This benchmark measures the behavior. Every cell is a **real headless Claude Code session**
(`claude -p`) editing a **seeded workspace**, scored on the pillar that cell targets.

## What is different from the single-shot bench

| | single-shot | agentic (this) |
|---|---|---|
| unit | one prompt to one completion | a Claude Code session in a temp workspace |
| baseline | bare model, prepended text | the **real agent** with no plugin (the fair baseline) |
| activation | text prepend | the **actual SessionStart hook** via `--plugin-dir` |
| measures | LOC + correctness | clarify, lean, optimal, economy, hygiene, sync, done-gate, safety |

## Arms

The headline comparison is **capybaraa vs the bare baseline** - nothing else. Three kinds:
`bare` (the unaided agent, the only thing capybaraa is scored against), `plugin` (capybaraa
itself, loaded via `--plugin-dir`), and `prompt` (a generic one-line instruction, an optional
reference point, not part of the headline read). Available:

`baseline` / `regular` (bare) · `capybaraa` (plugin, **on**) · `yagni` · `yagni-oneliner` ·
`concise` (prompt).

Default `--arms` is `baseline,capybaraa`. The prompt arms are honest controls: if a one-line
instruction matches the plugin on some axis, the benchmark should show it. capybaraa resolves
to this repo (override with `CAPYBARAA_PLUGIN_DIR`).

## Isolation (why the baseline is trustworthy)

Capybaraa activates from a `SessionStart` hook. If that hook fires on every arm, the baseline
is secretly running capybaraa and the whole comparison is contaminated. Three guards:

1. `--setting-sources project,local` excludes the user's globally-installed plugins from
   every arm.
2. only the `capybaraa` arm gets `--plugin-dir <repo>`, loading exactly this plugin.
3. every cell gets its **own** `CLAUDE_CONFIG_DIR`, so a stale `off` flag in your real
   `~/.claude/.capybaraa-active` cannot neuter the treatment. The capybaraa arm runs with
   `CAPYBARAA_DEFAULT_LEVEL=on`.

Each cell records an `activated` field read back from its isolated flag file: the `capybaraa`
arm should show `on`, the others empty. That is the proof the hook fired for the right arm
and only that arm.

## Tasks (covering every pillar)

| id | pillar | the job | signal measured |
|---|---|---|---|
| `clarify-settings` | CLARIFY | "Add user settings persistence" (ambiguous) | judge: asked the key questions vs assumed; `premature_files` written |
| `clarify-export` | CLARIFY | "Add an export button" (ambiguous) | same |
| `lean-reuse` | LEAN | add a slug field; repo already has `utils/slugify.js` | reused the helper vs reimplemented / added a dep |
| `lean-native` | LEAN | add a date field to a form | `<input type="date">` vs a date-picker lib / hand-rolled widget |
| `optimal-members` | OPTIMAL | `count_shared(a, b)` over large lists | promoted `b` to a set (O(n)) vs list-membership in a loop (O(n*m)) |
| `economy-nofiller` | ECONOMY | implement a 1-line `to_cents` | clean vs comment lines outnumbering the code |
| `sync-rename` | SYNC | rename `getLevel` → `getState` | every reference updated, comment included, vs a stale leftover |
| `hygiene-replace` | HYGIENE | rewrite a field splitter for quoted fields | replaced the old helper vs piled a v2 beside it |
| `complete-fixtest` | COMPLETE | "make the failing test pass" | did the agent **run** the test (`ran_check`); does it actually pass |
| `safe-path` | SAFETY | implement `safe_join` | `../../etc/passwd` must not escape |
| `safe-email` | SAFETY | implement `is_valid_email` | newline-injection address must be rejected |
| `feat-rating` / `feat-export` / `feat-palette` | LEAN (open) | build a small UI feature | LOC for over-build + completeness judge |

The SAFETY tier is the guardrail: it proves "leaner" never means "dropped a guard". Each
safety task's `bad` reference is the lazy-but-plausible version, correct on the happy path,
unsafe on the adversarial input, exactly the code a binary correctness gate would pass.

## Metrics

- **correct / safe** (gates): the produced code is executed against normal and adversarial input.
- **reuse / native / optimal / economy / sync / hygiene** (gates): deterministic checks of the produced files.
- **ran_check**: parsed from the session transcript (did the agent run a test command).
- **clarify score** (judge, 0-3): `judge.py`, fixed model at temp 0, published rubric, every
  verdict names which clarifications were asked and which were missed.
- **src_loc / src_files / cost / duration**: straight from the produced files and the CLI JSON.

Every deterministic instrument ships a `good` and a `bad` reference and is checked by
`--selftest` (good must pass, bad must be caught) **before any API call**.

## Reproduce

Needs the `claude` CLI (this is the harness, no SDK), Python 3, and an authenticated Claude Code.

```bash
cd benchmarks/agentic
python3 run.py --selftest            # prove the instruments, no API. run first.
python3 judge.py --selftest-offline  # prove the judge gate logic, no API

# live (spends API), all tasks, baseline vs capybaraa, Haiku, 3 runs each:
python3 run.py --all --arms baseline,capybaraa --models haiku --runs 3 --workers 6
python3 judge.py --run runs/<stamp>  # score the CLARIFY tier

python3 judge.py --complete-run runs/<stamp>  # completeness of the open feature tasks
python3 run.py --rescore runs/<stamp>   # recompute deterministic metrics offline, no API
python3 chart.py runs/<stamp> ../../assets/benchmark.svg   # redraw the README chart from the run
```

Agents only write code: `--strict-mcp-config` removes the browser, and `Bash` is blocked
except on `complete-fixtest`, where running the test is the whole point. Cells are fully
isolated, so `--workers N` runs N at once. Workspaces are kept under `runs/<stamp>/`, so any
metric change is re-applied offline with `--rescore`; you never pay the API twice for a
measurement tweak.

### Read it right

Pair the LOC numbers with the gates. A low-LOC arm whose `correct`/`safe`/`native`/`reuse`
also drop is doing **less**, not less-bloated, and the benchmark is built to catch that. If
the arms converge (everyone safe, similar size, everyone asks), it says so. It can disprove
the plugin's value, not only confirm it.

## What this can and cannot show

- It **can** show, on real multi-file sessions, whether capybaraa asks before coding, reuses
  what exists, prefers native, replaces instead of piling on, runs its done-gate, and keeps
  its guards while staying lean.
- It **cannot** claim production-readiness from this handful of tasks, and a deterministic safety check
  is a floor, not a security proof. The CLARIFY tier leans on an LLM judge, made auditable but
  still a model judging a model.

## Results

Latest: [`../results/2026-06-25-sonnet-0.4.0.md`](../results/2026-06-25-sonnet-0.4.0.md) (Sonnet
4.6, 3 runs). Write each run up under `../results/` dated, with the per-task table; only paste
numbers into the top-level README once you have actually run it.
