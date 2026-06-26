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

The ticket: "add a settings page."

**A stock agent** guesses what you meant and starts typing. It invents a `SettingsManager`, a `ConfigProvider`, three new files, and a migration, before it knows which settings you even want. Most of that is scaffolding for things you never asked for, and you only find out it guessed the spec wrong once it's all written.

**Capybaraa** stops and asks the two questions that actually decide the design, with the choices drawn so the tradeoff is obvious at a glance:

```
🦫 two questions before I touch code:

   ┌── settings ──┐
   │ theme        │   store where?   local / your API / both
   │ language     │   per-device, or synced to the account?
   └──────────────┘

   1. just these two fields now, or more coming?
   2. per-device, or synced?

   edge cases I'll handle: no-JS fallback, unknown saved value, first load.
```

Then it builds the smallest thing that fits your answers, runs the check, and stops. No `SettingsManager`, no files you didn't need, nothing left half-done.

That is the whole pitch: **ask first, build only what the answer needs, prove it works, leave it clean.** The rest of this README is how it does that, and the numbers that show it.

## The seven pillars

> **The capybaraa way:** understand the prompt, gather real context, learn the
> codebase, explore the actual flow. For anything past a trivial ask, clarify
> before coding: ask the curated questions you need (ASCII on the options), then
> write the real root-cause fix. Never patchwork. When you're done, leave the docs
> and tests as honest about the code as the code itself.

| Pillar | What it enforces |
|--------|------------------|
| **CLARIFY** | Understand and explore first, then ask what's left: as many curated questions as the task actually needs (one or a dozen, never a fixed quota). Any question with a shaped choice carries a small ASCII sketch on the options - near-mandatory, skipped only for a pure yes/no - plus explicit edge cases. Don't guess the spec. |
| **LEAN** | The YAGNI ladder: does it need to exist? reuse what's here? stdlib? native? one line? then minimal code. |
| **OPTIMAL** | Right data structure, best feasible time and space, no needless O(n^2). |
| **ECONOMY** | Terse output, no useless comments or filler, minimal tokens, no over-exploring. |
| **COMPLETE** | Finish terminally, root cause not symptom, and run the check before claiming done. |
| **HYGIENE** | Refactor means replace, not pile-on. Delete dead code and stale comments, sanitize inputs, mark deliberate simplifications with a `capybaraa:` note, flag security. Out-of-scope finds get surfaced, not silently changed. |
| **SYNC** | A change isn't done until everything that named the old shape catches up: docs, README, comments, tests, sibling callers, version strings. Update them in the same pass and delete the stale; `/capybaraa-sync` sweeps the whole repo on demand. |

Above all seven sits the **conscious gate**: before any token-expensive move, capybaraa checks the spend is proportional to the ask - small task, just do it; scope unclear and a wrong guess is costly, ask one question first.

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

## Does it actually help? (real numbers)

Yes, and we measured it instead of asserting it. The [agentic benchmark](benchmarks/agentic/) runs real headless Claude Code sessions (`claude -p`) in throwaway workspaces and compares **capybaraa against the bare agent with no plugin**, one task per pillar. Same model, same task, the only difference is whether capybaraa is on, so any gap is the plugin.

**Sonnet 4.6, 3 runs per cell.** Three things came out of it:

<p align="center">
  <img src="assets/benchmark.svg" width="720" alt="Two charts. Top: median lines of code per task, baseline vs capybaraa, lower is leaner. Star rating 38 vs 23 (-39%), CSV export 20 vs 15 (-25%), Cmd-K palette 89 vs 78 (-12%), rewrite CSV parser 17 vs 16 (-6%), fix failing test 4 vs 2 (-50%); every one scored fully complete 3 of 3. Bottom: CLARIFY judge 0 to 3, baseline 0 of 3, capybaraa 1.5 of 3; baseline built on assumptions including a 238-line SettingsManager while capybaraa wrote 0 lines and asked first; the 9 deterministic gates are 100% for both.">
</p>

**1. It asks before it builds.** Handed an underspecified ticket ("add user settings persistence to this app"), the bare agent dove straight into code on its own guesses, in one run writing a **238-line `SettingsManager`** for a spec nobody had pinned down. Capybaraa wrote **zero lines and asked the questions first**. On the CLARIFY judge (0-3, graded by a separate model with no plugin loaded) capybaraa scored **1.5 vs the baseline's 0**.

**2. It builds the same feature with less code.** On five tasks where there was real room to be leaner, capybaraa was **6-50% smaller** (a star-rating widget: 23 lines vs 38). Crucially, the completeness judge scored **every one fully complete, 3/3, for both arms**, so this is leaner, not less. It does cost a little more time and money per task, the price of asking and running the check.

**3. It never traded that for correctness.** On the nine deterministic gates (correct, safe, reuse a helper, use the native input, right data structure, no filler comments, keep docs in sync, replace not pile-on, run the test), **both arms passed 100%**. With a strong model the bare agent already nails these surgical tasks, and capybaraa holds that ceiling while adding the asking and the leanness on top.

The honest caveats: a handful of tasks on one model, so read it as directional, not a leaderboard. The CLARIFY tier leans on an LLM judge (made auditable: fixed model, published rubric, every verdict lists what was asked and missed), and a deterministic safety check is a floor, not a security proof.

### Run it yourself

You need the `claude` CLI and Python 3. From `benchmarks/agentic/`:

```bash
python3 run.py --selftest                                    # prove every scorer offline, spends nothing
python3 run.py --all --arms baseline,capybaraa --models sonnet --runs 3   # the live run (uses the API)
python3 judge.py --run runs/<stamp>           # CLARIFY score
python3 judge.py --complete-run runs/<stamp>  # completeness of the open feature tasks
python3 chart.py runs/<stamp> ../../assets/benchmark.svg   # redraw the chart above
```

`--selftest` runs first on purpose: every gate ships a good and a bad reference and must pass the good and catch the bad before a single API call. Full method, per-task table, and the isolation guarantees are in [`benchmarks/agentic/`](benchmarks/agentic/).

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

The seven pillars are always on, there's no command to run them. Once installed, capybaraa applies to every task automatically. The slash commands are just for on/off, review, audit, sync, and help:

| Command | What it does |
|---------|--------------|
| `/capybaraa [on \| off]` | Turn it on or off. No argument explains it and shows the current state. |
| `/capybaraa-review` | Review the current diff against the seven pillars. Lists findings, doesn't edit. |
| `/capybaraa-audit` | Scan the whole repo against the seven pillars, and harvest the `capybaraa:` deferral ledger. Ranked findings, doesn't edit. |
| `/capybaraa-sync` | Fix drift between the code and its docs/tests/refs after a change. Lists, confirms, then updates and deletes stale. |
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
