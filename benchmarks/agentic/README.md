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
| measures | LOC + correctness | LOC, output tokens, cost, time, completeness, plus per-behavior tiers (ask, lean, optimal, terse, clean, sync, safety) |

## Arms

The honest comparison puts capybaraa next to its peers, each loaded the way it actually ships,
all measured against the **bare baseline**. Three kinds:

- `bare` - the unaided agent, the reference everything is scored against.
- `plugin` - a SessionStart-hook plugin loaded via `--plugin-dir`. `capybaraa` resolves to this
  repo (override with `CAPYBARAA_PLUGIN_DIR`) and pins its activation flag on for the run;
  `ponytail` resolves to the installed plugin cache (override with `PONYTAIL_PLUGIN_DIR`) and is
  active by default on load, so it carries no flag.
- `prompt` - a system-prompt instruction via `--append-system-prompt`. `caveman` is benchmarked
  this way because it ships as a skill, not a plugin; its SKILL is vendored at `caveman-SKILL.md`
  (MIT) and loaded as the system prompt, matching how ponytail benchmarks its own caveman control.
  `yagni` / `yagni-oneliner` / `concise` are one-line reference instructions.

Available: `baseline` / `regular` (bare) · `capybaraa` (plugin, **on**) · `ponytail` (plugin) ·
`caveman` (prompt, vendored) · `yagni` · `yagni-oneliner` · `concise` (prompt).

Default `--arms` is `baseline,capybaraa`. The four-arm headline run is
`baseline,caveman,ponytail,capybaraa`. caveman is the key control: if the win were just
"talk less," caveman (a pure prose-compression skill) would match capybaraa. It does not.

**Prereq for the peer arms:** ponytail must be installed (`/plugin install ponytail`) or
`PONYTAIL_PLUGIN_DIR` exported; caveman needs nothing, it is vendored. A plugin arm that cannot
be resolved fails the run early rather than silently degrading to baseline.

## Isolation (why the baseline is trustworthy)

Capybaraa and ponytail activate from a `SessionStart` hook. If a hook fires on every arm, the
baseline is secretly running a plugin and the whole comparison is contaminated. The guards:

1. `--setting-sources project,local` excludes the user's globally-installed plugins from
   every arm, so nothing loads that an arm didn't ask for.
2. each `plugin` arm gets `--plugin-dir <dir>` for **exactly its own** plugin (capybaraa's repo,
   or ponytail's installed cache); bare and prompt arms get none.
3. for the run, the capybaraa arm's flag (`~/.claude/.capybaraa-active`) is pinned `on` and
   `CAPYBARAA_DEFAULT_LEVEL=on` is set, so a stale `off` in your real config cannot neuter the
   treatment; the original flag is restored when the run finishes. ponytail and caveman are
   active by default, so they need no pin.

The capybaraa arm records an `activated` field read back from its flag (`on`); the others are
empty (ponytail/caveman activation is confirmed behaviorally instead, by their output differing
from baseline, which the smoke run checks before any full matrix). That is the proof each arm
ran as itself and not as the baseline.

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

# live (spends API). the four-arm headline run, two batches kept separate:
#   build axis (everyone builds; LOC / tokens / cost / time / completeness):
python3 run.py --task feat-rating,feat-export --arms baseline,caveman,ponytail,capybaraa --models sonnet --runs 2
python3 judge.py --complete-run runs/<build-stamp>
#   clarify axis (ambiguous; who asks vs guesses). caveman dropped, it is a prose skill:
python3 run.py --task clarify-settings,clarify-export --arms baseline,ponytail,capybaraa --models sonnet --runs 2
python3 judge.py --run runs/<clarify-stamp>

# fold the clarify scores into the build run, then draw the chart:
cp runs/<clarify-stamp>/clarify.json runs/<build-stamp>/clarify.json
python3 run.py --rescore runs/<build-stamp>   # recompute deterministic metrics offline, no API
python3 chart.py runs/<build-stamp> ../../assets/benchmark.svg   # redraw the README chart
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

- It **can** show, on real multi-file sessions, whether capybaraa spends fewer tokens and writes
  less code than a bare agent while staying complete, asks before coding on an ambiguous ticket,
  reuses what exists, and keeps its guards while staying lean.
- It **cannot** claim production-readiness from this handful of tasks, and a deterministic safety check
  is a floor, not a security proof. The CLARIFY and completeness tiers lean on an LLM judge, made
  auditable but still a model judging a model.

## Results

Latest: [`../results/2026-06-26-haiku-honest.md`](../results/2026-06-26-haiku-honest.md) (Haiku 4.5,
four arms, n=3, with the safety tier; capybaraa is the leanest arm on code and fully safe, but
spends more output tokens and cost than the bare agent on these small tasks). Cross-model:
[`../results/2026-06-26-sonnet-lean.md`](../results/2026-06-26-sonnet-lean.md) (Sonnet 4.6, n=2,
where output tokens came in under baseline). Earlier: the [four-arm clarify run](../results/2026-06-26-sonnet-4arm.md)
and the broader [0.4.0 run](../results/2026-06-25-sonnet-0.4.0.md) covering the deterministic
gates. Write each run up under `../results/` dated, with the per-task table; only paste numbers
into the top-level README once you have actually run it.
