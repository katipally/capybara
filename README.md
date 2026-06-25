<p align="center">
  <img src="assets/capybara_nobg.png" width="200" alt="Capybaraa">
</p>

<h1 align="center">Capybaraa</h1>

<p align="center">
  <em>The chillest senior dev in the swamp. Doesn't panic, doesn't over-build. Asks first, ships clean, leaves.</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Claude%20Code-plugin-8a6d3b?style=flat-square" alt="Claude Code plugin">
  <img src="https://img.shields.io/badge/license-MIT-8a6d3b?style=flat-square" alt="MIT license">
  <img src="https://img.shields.io/badge/levels-low%20·%20medium%20·%20high-8a6d3b?style=flat-square" alt="Levels">
</p>

You know the type. Unbothered, has seen every framework rise and fall and didn't migrate to any of them. You hand over a vague ticket and fifty lines of someone's first draft. He reads it, asks the two questions that actually matter, draws a little box-and-arrow on a napkin, and replaces the whole thing with the part you needed.

Capybaraa puts that habit inside Claude Code.

It's the half of "good engineering" that agents skip: think before you type, then leave the place clean. It makes the agent clarify the spec before it writes code, pick the right complexity, stop padding output, actually verify "done", and not leave dead code and stale comments behind.

## Before and after

You ask for "add a settings page." A stock agent invents a `SettingsManager`, a `ConfigProvider`, three new files, a migration, and starts coding before it knows what settings you even mean.

With capybaraa it clarifies before it writes code:

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

> **The capybaraa way:** understand the prompt, gather real context, learn the
> codebase, explore the actual flow. For anything past a trivial ask, clarify
> before coding: ask the curated questions you need (ASCII on the options), then
> write the real root-cause fix. Never patchwork.

| Pillar | What it enforces |
|--------|------------------|
| **CLARIFY** | Understand and explore first, then for non-trivial work clarify before coding: as many curated questions as the task actually needs (one or a dozen, never a fixed quota), a small ASCII sketch on the options, explicit edge cases. Don't guess the spec. |
| **LEAN** | The YAGNI ladder: does it need to exist? reuse what's here? stdlib? native? one line? then minimal code. |
| **OPTIMAL** | Right data structure, best feasible time and space, no needless O(n²). |
| **ECONOMY** | Terse output, no useless comments or filler, minimal tokens, no over-exploring. |
| **COMPLETE** | Finish terminally, root cause not symptom, and run the check before claiming done. |
| **HYGIENE** | Refactor means replace, not pile-on. Delete dead code and stale comments, sanitize inputs, flag security. Out-of-scope finds get surfaced, not silently changed. |

The point was never "fewest tokens." It's: do exactly what the task needs, understand it first, and never cut validation, error handling, security, or accessibility. The code ends up small because it's necessary, not golfed.

## How it works

One source of truth, [`principles/build-instructions.js`](principles/build-instructions.js), injected every session by a `SessionStart` hook and into every subagent by a `SubagentStart` hook. Your level lives in a flag file (`~/.claude/.capybaraa-active`).

It's proportional, on purpose:

```
 ALWAYS-ON  the 6 pillars as terse rules. prompt-cached, ~free per turn.
 ON DEMAND  the clarify-with-ASCII questions and the run-the-check done-gate
            kick in only when the task is big enough to earn them.
```

A one-line fix gets the rules and nothing else: no ceremony, no token burst. A real feature gets the full treatment: the agent clarifies before it writes code, and plan mode is the ideal place for that when you're in it.

## Does it actually help? (numbers)

The honest answer: capybaraa's value is behavioral, so it shows up in a real agent session, not a one-shot line count. The [agentic benchmark](benchmarks/agentic/) runs actual headless Claude Code sessions on seeded workspaces, three arms (bare baseline, capybaraa, and a "just be concise" one-liner), and scores each on the pillar it targets.

From the first agentic run (Sonnet 4.6, n=3, [full writeup](benchmarks/results/2026-06-25-agentic-sonnet.md)):

```
 CLARIFY (judge 0-3)   capybaraa 3.0  >  baseline 2.5  >  "be concise" 2.0
                       it asks the questions a senior dev needs, before coding
 LEAN  (over-build)    star rating 32 -> 25 LOC (-22%), palette 90 -> 82, export 19 -> 17
                       and the completeness judge scores it 3/3: leaner, still fully built
 SAFETY / correctness  100% across every arm; capybaraa never traded a guard for fewer lines
 COST                  ~5-15% more per task: the price of asking + checking more
```

The point isn't "fewest lines." It's that capybaraa clarifies more, builds leaner without shipping a stub, and stays safe, and it beats a bare "be concise" instruction at all three. Every gate ships a good/bad reference and is validated before any API spend; the judges are auditable (fixed model, published rubric, self-validated). Methodology, isolation, and caveats are in [`benchmarks/agentic/README.md`](benchmarks/agentic/README.md).

Run it yourself (needs the `claude` CLI and Python 3):

```bash
cd benchmarks/agentic
python3 run.py --selftest                                                  # prove the instruments, no API
python3 run.py --all --arms baseline,capybaraa,concise --models sonnet --runs 3
python3 judge.py --run runs/<stamp> && python3 judge.py --complete-run runs/<stamp>
```

There's also an older single-shot LOC bench under [`benchmarks/`](benchmarks/) (`promptfooconfig.yaml`); it only measures lines, the one dimension capybaraa barely moves, so prefer the agentic one.

## Install

Capybaraa is a native Claude Code plugin, installed from this repo:

```
/plugin marketplace add katipally/capybaraa
```
```
/plugin install capybaraa@capybaraa
```
(Two separate prompts.) Needs `node` on your PATH for the lifecycle hooks. Without it the skills still work, the always-on activation just stays quiet. Start a new session after installing so the skills load.

## Levels

```
/capybaraa low | medium | high | off          "stop capybaraa" also turns it off
```

| `low` | nudges only: build it, name the leaner option in one line |
| `medium` *(default)* | all pillars, proportional; clarify before code when the task warrants it |
| `high` | aggressive: max questioning, deletion first, strict done-gate |

The level shows in your statusline as `[CAPYBARAA]` or `[CAPYBARAA:HIGH]`. Set a default for every session with `CAPYBARAA_DEFAULT_LEVEL` (`low`/`medium`/`high`/`off`) or `defaultLevel` in `~/.config/capybaraa/config.json`. Default is `medium`.

## Commands

The six pillars are always on, there's no command to run them. Once installed, capybaraa applies to every task automatically. The slash commands are just for intensity, review, and help:

| Command | What it does |
|---------|--------------|
| `/capybaraa [low \| medium \| high \| off]` | Set the intensity, or turn it off. No argument means medium. |
| `/capybaraa-review` | Review the current diff against the six pillars. Lists findings, doesn't edit. |
| `/capybaraa-audit` | Scan the whole repo against the six pillars. Ranked findings, doesn't edit. |
| `/capybaraa-help` | Quick reference card. |

They're plugin skills, so they may show up namespaced as `/capybaraa:capybaraa` in the menu. Skills load at session start, so start a new session after installing.

## Develop and test locally

```bash
git clone https://github.com/katipally/capybaraa && cd capybaraa
node test/smoke.js                 # the runnable checks (principles, parsing, skills)
claude --plugin-dir .              # load the plugin without installing
claude plugin validate .           # validate the manifest (Claude Code CLI)
```

## Uninstall

`/plugin remove capybaraa`

## FAQ

**Does it slow every task down with questions?**
No. Trivial asks get the rules and nothing else. The questions and the done-gate only fire when the task is big or ambiguous enough to need them.

**Do I need a config file?**
No. `CAPYBARAA_DEFAULT_LEVEL` or `~/.config/capybaraa/config.json` can set a default level, but nothing is required.

**Why a capybaraa?**
Calmest animal alive, gets along with everything, wastes zero energy. You already knew.

## License

[MIT](LICENSE).
