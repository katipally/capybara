<h1 align="center">🦫 Capybara</h1>

<p align="center">
  <em>The chillest senior dev in the swamp. Doesn't panic, doesn't over-build. Asks first, ships clean, leaves.</em>
</p>

<p align="center">
  <img src="https://img.shields.io/npm/v/@katipally/capybara?style=flat-square&color=8a6d3b&label=npm" alt="npm">
  <img src="https://img.shields.io/badge/works%20with-4%20tools-8a6d3b?style=flat-square" alt="Works with 4 tools">
  <img src="https://img.shields.io/badge/license-MIT-8a6d3b?style=flat-square" alt="MIT license">
  <img src="https://img.shields.io/badge/levels-low%20·%20medium%20·%20high-8a6d3b?style=flat-square" alt="Levels">
</p>

You know the type. Unbothered, has seen every framework rise and fall and didn't migrate to any of them. You hand over a vague ticket and fifty lines of someone's first draft. He reads it, asks the two questions that actually matter, draws a little box-and-arrow on a napkin, and replaces the whole thing with the part you needed.

Capybara puts that habit inside your AI agent.

It's the half of "good engineering" that agents skip: think before you type, then leave the place clean. It makes the agent clarify the spec before it writes code, pick the right complexity, stop padding output, actually verify "done", and not leave dead code and stale comments behind.

## Before and after

You ask for "add a settings page." A stock agent invents a `SettingsManager`, a `ConfigProvider`, three new files, a migration, and starts coding before it knows what settings you even mean.

With capybara it drops into plan mode first:

```
🦫 a couple of questions before I touch code:

   ┌─ settings ─┐
   │ theme      │  persisted where?
   │ ...        │  (localStorage / your API / both)
   └────────────┘

   1. Just theme for now, or more fields coming?
   2. Per-device, or synced to the account?

   edge cases I'll handle: no-JS fallback, unknown stored value, first load.
```

Then it writes the smallest thing that answers your actual answers, and runs the check before it says it's done.

## The six pillars

> **The capybara way:** understand the prompt, gather real context, learn the
> codebase, explore the actual flow. For anything past a trivial ask, drop into
> plan mode, ask the curated questions you need (ASCII on the options), then write
> the real root-cause fix. Never patchwork.

| Pillar | What it enforces |
|--------|------------------|
| **CLARIFY** | Understand and explore first, then for non-trivial work use plan mode: as many curated questions as the task actually needs (one or a dozen, never a fixed quota), a small ASCII sketch on the options, explicit edge cases. Don't guess the spec. |
| **LEAN** | The YAGNI ladder: does it need to exist? reuse what's here? stdlib? native? one line? then minimal code. |
| **OPTIMAL** | Right data structure, best feasible time and space, no needless O(n²). |
| **ECONOMY** | Terse output, no useless comments or filler, minimal tokens, no over-exploring. |
| **COMPLETE** | Finish terminally, root cause not symptom, and run the check before claiming done. |
| **HYGIENE** | Refactor means replace, not pile-on. Delete dead code and stale comments, sanitize inputs, flag security. Out-of-scope finds get surfaced, not silently changed. |

The point was never "fewest tokens." It's: do exactly what the task needs, understand it first, and never cut validation, error handling, security, or accessibility. The code ends up small because it's necessary, not golfed.

## How it works

One source of truth, [`principles/build-instructions.js`](principles/build-instructions.js), injected every session by a `SessionStart` hook and into every subagent by a `SubagentStart` hook. Your level lives in a flag file (`~/.claude/.capybara-active`).

It's proportional, on purpose:

```
 ALWAYS-ON  the 6 pillars as terse rules. prompt-cached, ~free per turn.
 PLAN MODE  the clarify-with-ASCII questions and the run-the-check done-gate
            kick in only when the task is big enough to earn them.
```

A one-line fix gets the rules and nothing else: no ceremony, no token burst. A real feature gets the full treatment through Claude Code's plan mode.

## Does it actually help? (numbers)

Short answer: there's a benchmark you can run yourself, and the results live in [`benchmarks/`](benchmarks/). We don't ship made-up numbers in this README. Run the suite against your own models and read the dated writeup it produces:

```bash
cd benchmarks
npx promptfoo eval -c promptfooconfig.yaml --output results/latest.json   # needs your model creds
node score.js results/latest.json                                        # LOC / cost / latency table
```

The harness pairs each task with a correctness gate, so a broken one-liner that "looks short" fails instead of scoring well. Methodology and caveats (what's executed vs. structurally checked, single-shot vs. agentic) are in [`benchmarks/README.md`](benchmarks/README.md). Once you've run it, the medians land in `benchmarks/results/` and you can quote them here.

## Install

### Claude Code (native plugin, recommended)

```
/plugin marketplace add katipally/capybara
```
```
/plugin install capybara@capybara
```
(Two separate prompts.) Needs `node` on your PATH for the lifecycle hooks. Without it the skills still work, the always-on activation just stays quiet.

### Cursor, Copilot, OpenCode (one-shot wizard)

Run in your project. It detects what you have and writes each tool's rules file:

```bash
npx @katipally/capybara init       # detect tools, install the rules
npx @katipally/capybara doctor     # show what's installed where
npx @katipally/capybara update     # refresh to the latest text
```

(After `npm i -g @katipally/capybara` it's just `capybara init`.)

## Levels

```
/capybara low | medium | high | off          "stop capybara" also turns it off
```

| `low` | nudges only: build it, name the leaner option in one line |
| `medium` *(default)* | all pillars, proportional; plan mode when the task warrants it |
| `high` | aggressive: max questioning, deletion first, strict done-gate |

The level shows in your statusline as `[CAPYBARA]` or `[CAPYBARA:HIGH]`. Set a default for every session with `CAPYBARA_DEFAULT_LEVEL` (`low`/`medium`/`high`/`off`) or `defaultLevel` in `~/.config/capybara/config.json`. Default is `medium`.

## Commands

The six pillars are always on, there's no command to run them. Once installed, capybara applies to every task automatically. The slash commands are just for intensity, review, and help:

| Command | What it does |
|---------|--------------|
| `/capybara [low \| medium \| high \| off]` | Set the intensity, or turn it off. No argument means medium. |
| `/capybara-review` | Review the current diff against the six pillars. Lists findings, doesn't edit. |
| `/capybara-help` | Quick reference card. |

They're plugin skills, so they may show up namespaced as `/capybara:capybara` in the menu. Skills load at session start, so start a new session after installing. The wizard-installed tools (Cursor, Copilot, OpenCode) get the same always-on rules.

## Develop and test locally

```bash
git clone https://github.com/katipally/capybara && cd capybara
node test/smoke.js                 # the runnable checks (principles, parsing, bridges)
claude --plugin-dir .              # load the plugin without installing
claude plugin validate .           # validate the manifest (Claude Code CLI)
```

To exercise the wizard without publishing: `node bin/capybara.js init` in a throwaway directory.

## Uninstall

| Host | Command |
|------|---------|
| Claude Code | `/plugin remove capybara` |
| Cursor / Copilot / OpenCode | `npx @katipally/capybara uninstall` (removes the rules it wrote) |

## FAQ

**Does it slow every task down with questions?**
No. Trivial asks get the rules and nothing else. The questions and the done-gate only fire when the task is big or ambiguous enough to need them.

**Do I need a config file?**
No. `CAPYBARA_DEFAULT_LEVEL` or `~/.config/capybara/config.json` can set a default level, but nothing is required.

**Why a capybara?**
Calmest animal alive, gets along with everything, wastes zero energy. You already knew.

## License

[MIT](LICENSE).
