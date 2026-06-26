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
  <img src="https://img.shields.io/badge/mode-one%20·%20always%20on-8a6d3b?style=flat-square" alt="Mode">
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

## The seven pillars

> **The capybaraa way:** understand the prompt, gather real context, learn the
> codebase, explore the actual flow. For anything past a trivial ask, clarify
> before coding: ask the curated questions you need (ASCII on the options), then
> write the real root-cause fix. Never patchwork. When you're done, leave the docs
> and tests as honest about the code as the code itself.

| Pillar | What it enforces |
|--------|------------------|
| **CLARIFY** | Understand and explore first, then for non-trivial work clarify before coding: as many curated questions as the task actually needs (one or a dozen, never a fixed quota), a small ASCII sketch on the options, explicit edge cases. Don't guess the spec. |
| **LEAN** | The YAGNI ladder: does it need to exist? reuse what's here? stdlib? native? one line? then minimal code. |
| **OPTIMAL** | Right data structure, best feasible time and space, no needless O(n²). |
| **ECONOMY** | Terse output, no useless comments or filler, minimal tokens, no over-exploring. |
| **COMPLETE** | Finish terminally, root cause not symptom, and run the check before claiming done. |
| **HYGIENE** | Refactor means replace, not pile-on. Delete dead code and stale comments, sanitize inputs, mark deliberate simplifications with a `capybaraa:` note, flag security. Out-of-scope finds get surfaced, not silently changed. |
| **SYNC** | A change isn't done until everything that named the old shape catches up: docs, README, comments, tests, sibling callers, version strings. Update them in the same pass and delete the stale; `/capybaraa-sync` sweeps the whole repo on demand. |

Above all seven sits the **conscious gate**: before any token-expensive move, capybaraa checks the spend is proportional to the ask — small task, just do it; scope unclear and a wrong guess is costly, ask one question first.

The point was never "fewest tokens." It's: do exactly what the task needs, understand it first, keep the repo honest about itself, and never cut validation, error handling, security, or accessibility. The code ends up small because it's necessary, not golfed.

## How it works

One source of truth, [`principles/build-instructions.js`](principles/build-instructions.js), injected every session by a `SessionStart` hook and into every subagent by a `SubagentStart` hook. Whether it's on lives in a flag file (`~/.claude/.capybaraa-active`).

There's one mode and it has everything. No `lean`/`deep` dial to pick: the depth adapts to the task on its own, governed by the **conscious gate**:

```
 ALWAYS-ON  the 7 pillars as terse rules. prompt-cached, ~free per turn.
 GATE       before any token-expensive move (deep exploration, subagents,
            a full clarify ceremony, long output) check the spend is
            proportional. small task -> just do it, no ceremony, no burst.
            scope unclear & a wrong guess is costly -> ask ONE question first.
 FULL       when the task earns it: clarify-before-code, ASCII on the
            options, every edge case, complete code, strict done-gate.
```

Same rules in every case; what adapts is the spend. A one-line fix gets the rules and nothing else, no token burst. A real feature or hard bug earns the full treatment. Plan mode, when you're in it, is the perfect place for the clarifying.

### You can see it working

So you never have to guess whether it is on, capybaraa signs its work. Every substantive reply opens with a badge and non-trivial work closes with a one-line sign-off of what it did under the pillars:

```
🦫 capybaraa

   ...the actual answer...

🦫 clarified the storage question, reused the existing helper, ran the check.
```

If you do not see the 🦫 badge, capybaraa is off (or the session predates install, start a new one). The statusline badge `[CAPYBARAA]` is the second tell.

## Does it actually help? (numbers)

The honest answer: capybaraa's value is behavioral, so it shows up in a real agent session, not a one-shot line count. The [agentic benchmark](benchmarks/agentic/) runs actual headless Claude Code sessions on seeded workspaces and scores each arm on the pillar it targets.

**Current single-mode run (Sonnet 4.6, n=2, [writeup](benchmarks/results/2026-06-25-sonnet-0.3.0.md)).** Three tasks, three arms, median lines of code (lower is leaner). Every arm stayed 100% correct, safe, and gate-passing:

<p align="center">
  <img src="assets/benchmark-loc.svg" width="720" alt="Grouped bar chart, median lines of code per task (lower is leaner) for three arms on Sonnet 4.6, n=2. lean-native: baseline 1, capybaraa 1, ponytail 1 (irreducible, all tie). hygiene-replace: baseline 23.5, capybaraa 16.0, ponytail 9.0. feat-rating: baseline 46.0, capybaraa 25.5, ponytail 17.5. capybaraa is leaner than baseline on both reducible tasks; ponytail is leaner still.">
</p>

```
 TASK (lower = leaner)   baseline   capybaraa   ponytail
 lean-native (native)        1          1          1      (irreducible, all tie)
 hygiene-replace             23.5       16.0       9.0    (capybaraa -32% vs baseline)
 feat-rating  (over-build)   46.0       25.5       17.5   (capybaraa -45% vs baseline)
```

The straight read: **capybaraa cuts over-build 32–45% against the bare baseline without dropping correctness, safety, or hygiene — but ponytail is leaner still on raw line count**, and capybaraa costs a little more time and money (the price of clarifying and checking). These three tasks are pure LOC, which is ponytail's home turf; capybaraa's pitch is leanness *without* cutting safety or completeness, plus the clarify-first behavior these LOC gates don't measure. n=2, one model, treat as directional.

An earlier, broader **five-arm run** (Haiku 4.5, n=3, against the older two-mode build — [full writeup](benchmarks/results/2026-06-25-multiarm-haiku.md)) added the dimensions LOC can't see: on a 0–3 CLARIFY judge, capybaraa and ponytail tied at 2.0 (both ask first) ahead of baseline 1.5 and a yagni-oneliner arm at 0.0 that silently assumed the spec; capybaraa was the only arm that wrote tests (33–67% of runs, every other arm 0%); all arms stayed 100% safe against adversarial input. Every gate ships a good/bad reference validated before any API spend, and the judges are auditable (fixed model, published rubric). An older single-shot Sonnet 4.6 run is [here](benchmarks/results/2026-06-25-agentic-sonnet.md).

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

## On / off

One mode, always on, no dial. The depth adapts to each task via the conscious gate, so there's nothing to pick. The command only toggles it.

```
/capybaraa on | off                   "stop capybaraa" also turns it off
```

It never cuts validation, security, error handling, or accessibility, whatever the task size. When it's on, your statusline shows `[CAPYBARAA]`. To make `off` the default for every session, set `CAPYBARAA_DEFAULT_LEVEL=off` or `defaultState` in `~/.config/capybaraa/config.json`. Default is on. (Legacy `lean`/`deep`/`medium` values from older versions still read as on.)

## Commands

The seven pillars are always on, there's no command to run them. Once installed, capybaraa applies to every task automatically. The slash commands are just for on/off, review, sync, debt, and help:

| Command | What it does |
|---------|--------------|
| `/capybaraa [on \| off]` | Turn it on or off. No argument explains it and shows the current state. |
| `/capybaraa-review` | Review the current diff against the seven pillars. Lists findings, doesn't edit. |
| `/capybaraa-audit` | Scan the whole repo against the seven pillars. Ranked findings, doesn't edit. |
| `/capybaraa-sync` | Fix drift between the code and its docs/tests/refs after a change. Lists, confirms, then updates and deletes stale. |
| `/capybaraa-debt` | Harvest the `capybaraa:` deferral ledger (intentional simplifications). Lists, doesn't edit. |
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
No. `CAPYBARAA_DEFAULT_LEVEL` or `~/.config/capybaraa/config.json` can set whether it starts on or off, but nothing is required.

**Why a capybaraa?**
Calmest animal alive, gets along with everything, wastes zero energy. You already knew.

## License

[MIT](LICENSE).
