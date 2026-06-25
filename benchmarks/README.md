# Capybara benchmark

The honest version: this measures one thing, single-shot code generation, and it's a
floor on capybara's value, not the whole story. The pillars that matter most (clarify
before code, finish terminally, leave the repo clean) show up in long agent sessions,
not in one prompt. So treat these numbers as "even on the easy case, does prepending
the principles help, and does it ever break correctness?" If you want the full picture,
run capybara in a real session on a real repo and compare diffs.

## What it does

For each task in `tasks.js`, promptfoo sends two prompts to each model:

- **baseline**: the bare task.
- **capybara**: the same task with the plugin's principle text prepended (pulled live
  from `principles/build-instructions.js`, so the benchmark tests what actually ships).

Every answer goes through two checks:

- **correctness** (`assert.js`): the code is extracted and run against real inputs. A
  short answer that doesn't work fails. This is the guardrail against "shorter but wrong."
- **loc** (`loc.js`): non-blank lines of the produced code, recorded as a metric.

`score.js` then reports median LOC, pass rate, median cost, and median latency per
variant, plus the capybara-vs-baseline reduction.

## Run it

You need creds for whatever models you list in `promptfooconfig.yaml`:

```bash
export ANTHROPIC_API_KEY=...                      # or whichever provider you use
cd benchmarks
npx promptfoo eval -c promptfooconfig.yaml --output results/latest.json
node score.js results/latest.json
```

Edit `providers:` in the yaml to match your keys, and bump `repeat:` for steadier
medians (more runs, more cost).

## What's measured vs. what's structural

- `email-validator`, `debounce`, `csv-column-sum`, `flatten`: the code is **executed**
  against test inputs. Real correctness.
- `date-input`: **structural** check (does it reach for the native `<input type="date">`
  instead of pulling a date-picker library?). This is the over-build trap; it can't be
  run, so it's matched on text.

## Caveats

- Single-shot generation overstates and understates at once: it can't show the
  clarify-first or done-gate wins, and the bare baseline often includes prose the
  capybara prompt is told to skip, which inflates the LOC gap. Read the gap as
  directional, not precise.
- Five tasks is a small suite. Add your own to `tasks.js` (give each a real `check`).
- Costs and latencies depend on the provider and the day. Re-run before quoting.

## Results

Write each run up in `results/` using `TEMPLATE.md`, dated. Don't paste numbers into
the top-level README until you've actually run it; the README links here on purpose.
