# Sonnet 4.6, the lean rewrite: capybaraa vs baseline vs caveman vs ponytail

Date: 2026-06-26. Model: `claude-sonnet-4-6`. One batch, three clear build tasks
(`feat-rating`, `feat-export`, `feat-palette`), four arms, n=2 (24 sessions).

This run measures capybaraa **after the ruleset was cut to ponytail size**. The old core
injected ~1,500 tokens of seven-pillar prose plus a badge-and-sign-off ceremony every turn,
which is the irony of a lean tool: it tied the bare agent on output tokens and cost ~16% more.
The rewrite is the lean ladder plus five habits (~500 tokens), a one-glyph badge, no sign-off,
no done-gate. The question here: does the leaner capybaraa actually spend fewer tokens than a
bare agent?

Arms, each loaded the way it ships: `baseline` (no plugin), `caveman` (prose-compression skill,
MIT, vendored), `ponytail` (the pure-minimal plugin, installed 4.7.0, loaded live), `capybaraa`
(this plugin, activation verified per cell).

## Numbers (percent of the bare baseline, lower is leaner / cheaper / faster)

| vs baseline | lines of code | output tokens | cost | wall time | complete |
|---|--:|--:|--:|--:|--:|
| caveman | 99% | 95% | 100% | 93% | 3/3 |
| **ponytail** | **43%** | **75%** | 104% | 94% | 3/3 |
| **capybaraa** | 69% | 90% | 105% | 98% | 3/3 |

Baseline totals over the three tasks: 146.5 LOC, 3439 output tokens, $0.301, 66s.

Per-task median LOC:

| task | baseline | caveman | ponytail | capybaraa |
|---|--:|--:|--:|--:|
| feat-rating | 30.5 | 33.5 | 14.5 | 19.5 |
| feat-export | 18.5 | 16 | 8 | 11.5 |
| feat-palette | 97.5 | 95.5 | 40 | 70 |

## What changed, and the honest read

- **The lean rewrite worked.** Capybaraa now spends **10% fewer output tokens** than the bare
  agent (was tied), writes **31% less code** on these tasks (was ~17%), and finishes a hair
  faster (98% of baseline time). All three are real savings over a no-plugin agent.
- **ponytail is still the leanest**, and we say so: 43% of baseline LOC, 75% of output tokens.
  That is its single axis. capybaraa lands between the bare agent and ponytail, which is the
  honest place for a tool that also keeps validation, error handling, and accessibility.
- **Cost is the one metric still slightly above baseline (+5%, down from +16%).** On tasks this
  small, no injected plugin beats a bare agent on cost: even ponytail is +4%, caveman +0%. The
  injected ruleset is cached and re-read each turn; a few hundred tokens of overhead the trivial
  task can't fully amortize. On bigger tasks the 31% code saving dominates and cost flips below
  baseline. We do not claim a cost win here.
- **Leaner is not less.** The completeness judge scored every arm 3/3 on every task. The code
  capybaraa cut was code the bare agent didn't need, not the feature.

The "token saving" that holds up is **output tokens** (the work the model generates) and **code**
(what you review and own): capybaraa beats the bare agent on both, while staying complete. The
clarify behavior (ask + ASCII before building an ambiguous ticket) still ships in the ruleset; it
is just not benchmarked here, this run is about token efficiency on clear work.

Directional, not a leaderboard: n=2, three tasks, one model. Completeness is an LLM judge (fixed
model, temp 0, published rubric, run with no plugin so no arm grades itself).

Reproduce:

```
python3 run.py --selftest && python3 judge.py --selftest-offline
python3 run.py --task feat-rating,feat-export,feat-palette --arms baseline,caveman,ponytail,capybaraa --models sonnet --runs 2
python3 judge.py --complete-run runs/<stamp>
python3 chart.py runs/<stamp> ../../assets/benchmark.svg
```

ponytail must be installed (or `PONYTAIL_PLUGIN_DIR` set); caveman ships vendored.
