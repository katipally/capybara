# Changelog

All notable changes to this project are documented here.
Format loosely follows [Keep a Changelog](https://keepachangelog.com).

## [0.3.1] - 2026-06-25

- **SYNC is now the seventh pillar.** Keeping the docs, tests, comments, sibling code, and
  version strings in step with a change is promoted from a clause inside COMPLETE to a
  first-class pillar with its own `references/principles.md` section, review/audit `sync:`
  tag, and help-card row. "Six pillars" is now "seven pillars" everywhere. `/capybaraa-sync`
  (added in 0.3.0) is the on-demand sweep for it.
- **Benchmark graphs refreshed.** Removed the two stale Haiku SVGs
  (`benchmark-multiarm.svg`, `benchmark-gates.svg`) that showed the old two-mode build, and
  replaced them with one accurate chart (`benchmark-loc.svg`) built from the current
  single-mode Sonnet 4.6 run. The README "does it help" section is reworked to lead with
  current numbers; the earlier five-arm findings are kept as text, honestly labelled.
- **Consistency pass.** Audited and aligned every place the pillars and rules are stated
  (CORE, references, README, all skills, help card, manifests, tests) so they tell one
  consistent story.

## [0.3.0] - 2026-06-25

- **One mode, no dial.** `lean`/`deep` are gone. Capybaraa is now a single always-on
  mode whose depth adapts to the task: a trivial ask gets the rules and nothing else, a
  real feature or hard bug earns the full clarify-before-code treatment. State is just
  `on`/`off`. `/capybaraa on|off`; legacy flags/env (`deep`, `lean`, `medium`) map to
  `on` so existing installs keep working. Statusline shows `[CAPYBARAA]`, badge is
  `🦫 capybaraa` (no mode suffix).
- **Conscious token gate.** A new reflex in front of the six pillars: before any
  token-expensive move (deep exploration, spawning subagents, a full clarify ceremony,
  long output), check that the spend is proportional. Small task: just do it. Scope
  unclear and a wrong guess is costly: ask one sharp question first instead of bursting
  tokens. Resolves "have everything" vs "don't waste".
- **Fixed a real bug: substring command matching.** Deactivation and command parsing
  matched the phrase *anywhere* in a message, so a message that merely quoted "stop
  capybaraa" or "normal mode" silently turned it off. Commands now require a whole-message
  match (root-cause fix, with regression checks in the smoke test).
- **Pillars broadened beyond coding** (new projects, existing code, bug-clearing,
  research, ops, writing) and framed as the antidotes to how a stock agent fails, with
  sharper root-cause guidance (fix the shared cause once, not the one symptom path).
- **New `/capybaraa-debt` skill + `capybaraa:` marker convention.** Intentional
  simplifications get a `capybaraa:` comment naming the ceiling and upgrade trigger; the
  skill harvests them into a ledger and flags the no-trigger ones as highest rot risk.
- **Sync is part of done + new `/capybaraa-sync` skill.** The COMPLETE pillar now treats a
  change as unfinished until the docs, comments, tests, sibling code, and version strings
  that referenced the old shape are updated and the stale ones deleted (confirming before
  large or risky propagation). `/capybaraa-sync` runs that drift sweep across the whole
  repo on demand: lists each gap, confirms, then updates and removes stale.
- **Note on benchmarks.** The dated `benchmarks/results/*.md` files predate this change
  and still describe the `deep` arm; they record past runs and are left as-is. The
  harness (`benchmarks/prompts.js`, `benchmarks/agentic/run.py`) is updated to the single
  mode.

## [0.2.4] - 2026-06-25

- **Two modes instead of three levels.** `low`/`medium`/`high` are replaced by two
  modes chosen on the detail/token tradeoff: **`lean`** (minimum tokens: build tight,
  ask only what blocks correctness, skip ASCII unless it stops the wrong build) and
  **`deep`** *(default)* (full clarify-before-code, ASCII on the options, every edge case,
  complete-but-minimal code, strict done-gate). The six pillars hold in both; `lean`
  saves tokens, never validation or security. `/capybaraa lean|deep|off`, statusline shows
  `[CAPYBARAA]` (deep) or `[CAPYBARAA:LEAN]`. Default flips from `medium` to `deep`.
- **Visible signal in responses.** Capybaraa now opens substantive replies with a
  `🦫 capybaraa · <mode>` badge and closes non-trivial work with a one-line sign-off of
  what it did under the pillars, so you can always tell it is active and shaping the
  answer. One line each, the only ceremony it adds to how the agent talks.
- **README benchmark graphs.** Added two SVG charts
  (`assets/benchmark-multiarm.svg`, `assets/benchmark-gates.svg`) built from the existing
  five-arm Haiku 4.5 run: the clarify-vs-lean tradeoff and the gate scoreboard.
- **Dropped a dead dependency.** Removed the unused `playwright` dependency (never
  imported); the plugin now ships with zero runtime dependencies, only the Node stdlib.

## [0.2.3] - 2026-06-25

- **Reframed "plan mode" to behavior.** The injected principles, skills, help card,
  and README no longer tell the agent to "drop into plan mode" (a user-controlled mode
  it cannot reliably self-enter). They now say "clarify before you code" and note plan
  mode as the ideal venue when the user is in it.
- **Two-layer detail.** Added [`references/principles.md`](references/principles.md):
  per-pillar worked examples, situation rules, edge cases, and do/don't tables. The
  injected CORE stays terse and points at it on demand, so adherence improves without
  taxing every session.
- **New `/capybaraa-audit` skill.** Whole-repo scan against the six pillars (the
  diff-only `/capybaraa-review` has a repo-wide counterpart now). Lists findings ranked
  by impact, does not edit.
- **Logo.** README now leads with `assets/capybara_nobg.png` instead of an emoji.
- **Removed stray em-dashes** from the docs, honoring the project's own plain-language
  rule.

## [0.2.2] - 2026-06-25

- **Claude Code only.** Dropped Cursor / Copilot / OpenCode support and the npm
  CLI that installed them (`bin/`, `installer/`). Those tools have no hook or
  skill system, so they only ever got static rules text; the project is now a
  focused native plugin. Removed the npm publish workflow, releases ship from
  this repo via the marketplace pin. See [RELEASING.md](RELEASING.md).

## [0.2.1] - 2026-06-25

- Renamed to **capybaraa** across the board (plugin, slash commands `/capybaraa`,
  skills, flag file, statusline badge). Plain `capybara` was already taken, so the
  doubled `a` is the consistent brand.

## [0.2.0] - 2026-06-24

- Capybaraa is now fully independent. Removed the ponytail detection and the
  LEAN-pillar dedupe; all six pillars ship every session regardless of what else
  is installed.
- CLARIFY now routes real work into Claude Code's plan mode instead of just hoping
  the model asks questions. The injected text and skills point at plan mode with
  curated ASCII questions.
- New `/capybaraa-review` skill: reviews the current diff against the six pillars
  and lists findings, one line each. Does not edit files.
- Added a reproducible benchmark harness under `benchmarks/` (tasks, correctness
  gate, LOC/cost/latency scoring) so impact can be measured, not asserted.
- Rewrote the principle text and docs in plain language. No em-dashes, no shipped
  tagline.

## [0.1.0] - 2026-06-24

Initial release.

- Six pillars injected proportionally: **clarify, lean, optimal, economy,
  complete, hygiene**.
- Levels `low` / `medium` / `high` / `off` (default `medium`), switched with
  `/capybaraa <level>` or "stop capybaraa".
- Skills: `/capybaraa` (level switch) and `/capybaraa-help`.
- SessionStart / UserPromptSubmit / SubagentStart hooks; statusline badge.
- Coexistence with ponytail (dropped the overlapping LEAN pillar when ponytail was
  active). Removed in 0.2.0.
- `npx capybaraa init|doctor|update|uninstall` wizard installing rules
  bridges into Claude Code, Cursor, Copilot, and OpenCode.
