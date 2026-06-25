# Agentic benchmark, 2026-06-25 (Sonnet 4.6, n=3)

Full agentic run on Sonnet: real headless `claude -p` sessions, three arms (`baseline`,
`capybaraa` at level high, `concise` = a "be concise, build the minimal thing" one-liner),
11 tasks, 3 runs each = 99 cells, plus the CLARIFY and completeness judges. Harness:
`benchmarks/agentic/`. Run stamp `20260625-053223`.

This adds the over-build-trap LOC tier the [Haiku run](2026-06-25-agentic.md) was missing.

## Headline

On Sonnet the difference is clean and consistent:

- **CLARIFY** (judge, 0-3 median): **capybaraa 3.0 > baseline 2.5 > concise 2.0**. Capybaraa
  asks the questions a senior dev needs before coding; the "be concise" one-liner asks the
  least and dives in.
- **LEAN, over-build traps**: capybaraa writes less on every feature where there is room to
  over-build, and the **completeness judge scores all arms 3/3**, so the cut is real leanness,
  not a stub:
  - star rating: **32 -> 25 LOC (-22%)**, worst-case 38 -> 27
  - command palette: 90 -> 82 LOC (-9%)
  - CSV export: 19 -> 17 LOC
  - the failing-test fix: 4 -> 2 lines
- **Safety and correctness hold**: every arm is 100% correct and 100% safe, and passes the
  reuse / native / hygiene / done-gate checks. Capybaraa never traded a guard for fewer lines.
- **Capybaraa beats the one-liner.** "Just tell it to be concise" matches on raw LOC but is
  worse at clarifying (2.0 vs 3.0) and dove straight into code on `clarify-export` in 2/3 runs.
  The plugin's value is not only fewer lines, it is asking first and staying safe while lean.

The cost of that rigor is real but small on Sonnet: capybaraa is ~5-15% more expensive per
task (it asks and explores more). No bloat appeared anywhere on Sonnet.

## Numbers (median over n=3)

LEAN over-build tier (LOC via git diff; completeness judge 0-3, all arms scored 3):

| task | baseline LOC | capybaraa LOC | concise LOC | built (judge) |
|---|---|---|---|---|
| feat-rating | 32 | **25** | 29 | 3 / 3 / 3 |
| feat-palette | 90 | **82** | 83 | 3 / 3 / 3 |
| feat-export | 19 | **17** | 15 | 3 / 3 / 3 |

Surgical tier (all arms converge, gates all 100%):

| task | pillar | baseline | capybaraa | concise | gate |
|---|---|---|---|---|---|
| lean-reuse | LEAN | 1 | 1 | 1 | reuse 100% |
| lean-native | LEAN | 1 | 1 | 1 | native 100% |
| hygiene-replace | HYGIENE | 17 | 16 | 17 | hygiene 100% |
| complete-fixtest | COMPLETE | 4 | **2** | 4 | ran_check 100%, correct 100% |
| safe-path | SAFETY | 7 | 7 | 7 | safe 100% |
| safe-email | SAFETY | 4 | 5 | 4 | safe 100% |

CLARIFY (judge 0-3 median over the two ambiguous tickets, n=6 each):

| arm | clarify score |
|---|---|
| capybaraa | **3.0** |
| baseline | 2.5 |
| concise | 2.0 |

Isolation held: every `capybaraa` cell read back `activated=high`; `baseline`/`concise` empty.

## What this establishes

- The over-build-trap tier shows the LEAN win the surgical tasks could not: when there is room
  to over-build, capybaraa builds less and still fully builds it (completeness 3/3).
- The clarify gap is the clearest single signal: capybaraa asks more before coding than both
  the bare baseline and the "be concise" prompt.
- The safety tier is the guard: leaner never meant unsafe here.

## What it does not

- Three feature tasks and six surgical ones are a small suite; treat the LOC percentages as
  directional. The CLARIFY and completeness numbers come from an LLM judge (auditable: fixed
  model, published rubric, self-validated full>stub and asked>assumed), but still a model
  judging a model.
- One model (Sonnet), n=3. Re-run with higher n and on other models before quoting hard
  percentages. Reproduce: `python3 run.py --all --arms baseline,capybaraa,concise --models sonnet --runs 5`.
