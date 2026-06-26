# Haiku 4.5, four arms: the honest small-task read

Date: 2026-06-26. Model: `claude-haiku-4-5`. Four arms, three clear build tasks
(`feat-rating`, `feat-export`, `feat-palette`) plus a two-task safety tier
(`safe-path`, `safe-email`), n=3 (72 sessions). This is the lean-ruleset capybaraa
(the ladder plus five habits, ~500-token core).

The question: on small real-agent tasks, does the leaner capybaraa sit within the bare
agent's token and cost budget? The honest answer here is **no on tokens and cost, yes on
code and safety**. We report it straight.

## Numbers (percent of the bare baseline, lower is leaner / cheaper / faster)

| vs baseline | lines of code | output tokens | cost | wall time | complete | safe |
|---|--:|--:|--:|--:|:--:|:--:|
| caveman | 116% | 100% | 107% | 100% | 3/3 | 100% |
| **ponytail** | **79%** | **97%** | 106% | 102% | 3/3 | 100% |
| **capybaraa** | **77%** | 109% | 113% | 102% | 3/3 | 100% |

Baseline totals over the three build tasks: 204 LOC, 5,605 output tokens, $0.116, 65s.

Per-task median LOC:

| task | baseline | caveman | ponytail | capybaraa |
|---|--:|--:|--:|--:|
| feat-rating | 41 | 55 | 54 | 48 |
| feat-export | 25 | 20 | 21 | 26 |
| feat-palette | 138 | 162 | 86 | 84 |

## The honest read

- **capybaraa is the leanest arm on code (77%)**, a hair ahead of ponytail (79%) and far
  under caveman (116%). The saving is real and concentrated in the task with room to
  over-build: `feat-palette`, 84 lines vs the bare agent's 138. It scored fully complete
  (3/3, median) on every build task, so the smaller diff is less bloat, not less feature.
- **It does not beat the bare agent on output tokens (109%) or cost (113%).** capybaraa
  writes less *code* but a bit more *prose* (the brief framing, the reasoning it shows),
  and its always-on ~500-token ruleset is re-read each turn. On tasks this small that
  overhead is not amortized, so total generation and cost land above baseline. The overage
  is concentrated in `feat-export` and `feat-rating`; on `feat-palette` capybaraa's tokens
  are actually below baseline.
- **This is the opposite of the earlier Sonnet run** (output tokens 90%, cost +5%; see
  `2026-06-26-sonnet-lean.md`). Model and task size decide it: on bigger work the code
  saving dominates and cost flips below baseline; on tiny Haiku tasks the plugin tax wins.
  We do not claim a token or cost win on this batch.
- **Safety held: 100% on both adversarial tasks for every arm.** Leaner never meant a
  dropped guard. The `hygiene-replace` gate also passed for every arm (replaced the old
  helper, did not pile a `v2` beside it).
- **caveman is the control.** A pure prose-compression skill does **not** get leaner on
  code (116% LOC); capybaraa's code saving is behavioral, not just "talk less."

Directional, not a leaderboard: n=3, three build tasks, one model. Completeness is an LLM
judge (fixed model, temp 0, published rubric, run with no plugin so no arm grades itself).

Reproduce:

```
python3 run.py --selftest && python3 judge.py --selftest-offline
python3 run.py --task feat-rating,feat-export,feat-palette,hygiene-replace,safe-path,safe-email \
  --arms baseline,caveman,ponytail,capybaraa --models haiku --runs 3
python3 judge.py --complete-run runs/<stamp>
python3 chart.py runs/<stamp> ../../assets/benchmark.svg
```

ponytail must be installed (or `PONYTAIL_PLUGIN_DIR` set); caveman ships vendored.
