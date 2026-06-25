# Changelog

All notable changes to this project are documented here.
Format loosely follows [Keep a Changelog](https://keepachangelog.com).

## [0.2.0] - 2026-06-24

- Capybara is now fully independent. Removed the ponytail detection and the
  LEAN-pillar dedupe; all six pillars ship every session regardless of what else
  is installed.
- CLARIFY now routes real work into Claude Code's plan mode instead of just hoping
  the model asks questions. The injected text and skills point at plan mode with
  curated ASCII questions.
- New `/capybara-review` skill: reviews the current diff against the six pillars
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
  `/capybara <level>` or "stop capybara".
- Skills: `/capybara` (level switch) and `/capybara-help`.
- SessionStart / UserPromptSubmit / SubagentStart hooks; statusline badge.
- Coexistence with ponytail (dropped the overlapping LEAN pillar when ponytail was
  active). Removed in 0.2.0.
- `npx @katipally/capybara init|doctor|update|uninstall` wizard installing rules
  bridges into Claude Code, Cursor, Copilot, and OpenCode.
