<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/capybara_nobg.png">
    <img src="assets/capybaraa.png" width="200" alt="Capybaraa">
  </picture>
</p>

<h1 align="center">Capybaraa</h1>

<p align="center">
  <em>The chillest senior dev in the swamp. Doesn't panic, doesn't over-build. Asks first, ships clean, leaves.</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Claude%20Code-plugin-3a3226?style=flat-square" alt="Claude Code plugin">
  <img src="https://img.shields.io/github/stars/katipally/capybaraa?style=flat-square&color=3a3226&label=stars" alt="GitHub stars">
  <img src="https://img.shields.io/github/v/release/katipally/capybaraa?style=flat-square&color=3a3226&label=release" alt="Release">
  <img src="https://img.shields.io/badge/license-MIT-3a3226?style=flat-square" alt="MIT license">
  <img src="https://img.shields.io/badge/mode-one%20·%20always%20on-3a3226?style=flat-square" alt="Mode">
</p>

<p align="center">
  <strong>~20% less code</strong> than a bare agent, fully complete and 100% safe on the adversarial tier &middot; plus the questions ponytail skips
</p>

You know the type. Unbothered, has seen every framework rise and fall and didn't migrate to any of them. You hand over a vague ticket and fifty lines of someone's first draft. He reads it, asks the two questions that actually matter, draws a little box-and-arrow on a napkin, and replaces the whole thing with the part you needed.

Capybaraa puts that habit inside Claude Code: ponytail's lean discipline plus a few things it skips. Ask the deciding question before building the wrong thing, pick the right data structure, write fewer comments, and sync the docs after a change. The ruleset stays tiny on purpose, a plugin that preaches lean while injecting a wall of rules every turn is the irony it avoids.

## Before / after

The ticket: "add user settings persistence."

Claude can already ask good questions here, that's what plan mode is for. But in a plain run it tends to guess the spec and start building, and you find out it guessed wrong once it is written. In our benchmark, on a ticket like this the bare agent wrote ~300 lines of a settings panel nobody specified; capybaraa wrote zero and asked first.

The asking is Claude's; **capybaraa's specific add is the ASCII sketch on the options.** When it asks, it draws the choices so the tradeoff is obvious at a glance (unless the choice is shapeless and a sketch adds nothing), and it leans on asking the deciding questions even outside plan mode rather than guessing:

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

Then it builds the smallest thing that fits your answers and stops. No invented spec, no files you didn't need, nothing left half-done. The rest is plain lean: reuse what's there, the right data structure, few comments, and a sync of the docs after.

That is the whole pitch: **ask when it's ambiguous, build lean, leave it clean.** The rest of this README is how it does that, and the numbers that show it.

## Numbers

We measured it instead of asserting it. The [agentic benchmark](benchmarks/agentic/) runs real headless Claude Code sessions (`claude -p`) in throwaway workspaces and puts capybaraa next to its honest peers: a **bare agent** (no plugin), **caveman** (a prose-compression skill), and **ponytail** (the pure-minimal plugin, loaded live). Same model, same task, same seed; the only change is the arm.

<p align="center">
  <img src="assets/benchmark.svg" width="760" alt="Grouped bar chart, every metric as a percent of the bare baseline on Haiku 4.5, lower is leaner. Lines of code: caveman 116%, ponytail 79%, capybaraa 77%. Output tokens: caveman 100%, ponytail 97%, capybaraa 109%. Cost: caveman 107%, ponytail 106%, capybaraa 113%. Wall time: caveman 100%, ponytail 102%, capybaraa 102%. Safety tier: baseline, caveman, ponytail, and capybaraa all 100%.">
</p>

| vs the bare baseline | lines of code | output tokens | cost | time | complete | safe |
|---|--:|--:|--:|--:|:--:|:--:|
| caveman | 116% | 100% | 107% | 100% | 3/3 | 100% |
| **ponytail** | **79%** | **97%** | 106% | 102% | 3/3 | 100% |
| **capybaraa** | **77%** | 109% | 113% | 102% | 3/3 | 100% |

Read it straight, no spin:

**1. capybaraa writes the least code, and stays complete and safe.** At 77% of the bare agent's lines it is the leanest arm, a hair under ponytail (79%) and far under caveman (116%), while scoring fully complete (3/3) and 100% on the adversarial safety tier. The saving is real bloat removed, not a dropped feature: most of it is `feat-palette`, 84 lines against the bare agent's 138.

**2. It does not beat the bare agent on output tokens or cost here: +9% tokens, +13% cost.** capybaraa writes less code but a bit more prose, and its always-on ~500-token ruleset is re-read each turn; on tasks this small that overhead is not amortized. caveman, a pure prose-compression skill, is the control: it does **not** get leaner on code (116%), so capybaraa's code saving is behavioral, not just "talk less."

**3. Model and task size decide the token story.** On the earlier Sonnet run the same metrics were favorable (output tokens 90%, cost +5%); on small Haiku tasks the plugin tax dominates instead. We do not claim a token or cost win on this batch; on bigger work the code saving dominates and cost flips below baseline.

Honest caveats: a small task set (n=3, three build tasks) on one model, so read it as directional, not a leaderboard. Completeness is an LLM judge (fixed model, temperature 0, published rubric, run with no plugin loaded so no arm grades itself). [Full writeup and the reproduce commands.](benchmarks/results/2026-06-26-haiku-honest.md)

## How it works

One source of truth, [`principles/build-instructions.js`](principles/build-instructions.js), injected every session by a `SessionStart` hook and into every subagent by a `SubagentStart` hook. Whether it's on lives in a flag file (`~/.claude/.capybaraa-active`). It is small on purpose, about 500 tokens, so the always-on cost stays near zero.

It is ponytail's lean ladder:

```
 1. does it need to exist?        if speculative, don't build it
 2. already in this codebase?     reuse it
 3. stdlib or the platform?       use it
 4. an installed dependency?      use it
 5. can it be one line?           make it one line
 6. only then                     the least code that works
```

plus five habits, the only things capybaraa adds over plain lean:

| Habit | What it does |
|--------|------------------|
| **ASK** | Claude already asks when a spec is ambiguous (plan mode, its question prompt). Capybaraa's add is the ASCII sketch on the options: when it asks, it draws the choices so the tradeoff is concrete, unless the choice is shapeless and a sketch adds nothing. Still ask only the questions that decide the build, not what the prompt or code already answers. |
| **OPTIMAL** | Right data structure, no needless O(n^2). Correctness and clarity first, no micro-optimizing without a reason. |
| **TERSE** | Few words, few comments. No filler prose, no restating the obvious, no comment the code already says. |
| **CLEAN** | Refactor means replace: rewrite in place and delete the dead code and stale comments you touch, no `v2` beside the old one. |
| **SYNC** | A change isn't done until the docs, README, comments, tests, and version strings that named the old shape catch up; `/capybaraa-sync` sweeps the whole repo on demand. |

It never drops a guard for fewer lines: input validation, error handling, security, and accessibility stay, whatever the task size. Lean is fewer lines you didn't need, never a missing check.

So you know it's on, substantive replies open with a `🦫`. That is the only ceremony; the statusline badge `[CAPYBARAA]` is the second tell. No badge means it's off (or the session predates install, start a new one).

## Install

Capybaraa is a native Claude Code plugin, installed from this repo:

```
/plugin marketplace add katipally/capybaraa
```
```
/plugin install capybaraa@capybaraa
```

(Two separate prompts.) Needs `node` on your PATH for the lifecycle hooks. Without it the skills still work, the always-on activation just stays quiet. Start a new session after installing so the skills load.

## Commands

One mode, always on, no dial. It scales to each task on its own, so there's nothing to pick. The rules apply to every task automatically; the slash commands are just for on/off, review, audit, sync, and help.

| Command | What it does |
|---------|--------------|
| `/capybaraa [on \| off]` | Turn it on or off. No argument explains it and shows the current state. `"stop capybaraa"` also turns it off. |
| `/capybaraa-review` | Review the current diff against the rules. Lists findings, doesn't edit. |
| `/capybaraa-audit` | Scan the whole repo for bloat and drift. Ranked findings, doesn't edit. |
| `/capybaraa-sync` | Fix drift between the code and its docs/tests/refs after a change. Lists, confirms, then updates and deletes stale. |
| `/capybaraa-help` | Quick reference card. |

It never cuts validation, security, error handling, or accessibility, whatever the task size. To make `off` the default for every session, set `CAPYBARAA_DEFAULT_LEVEL=off` or `defaultState` in `~/.config/capybaraa/config.json`. Default is on. (Legacy `lean`/`deep`/`medium` values from older versions still read as on.) The commands are plugin skills, so they may show up namespaced as `/capybaraa:capybaraa`; start a new session after installing so they load.

## Development

```bash
git clone https://github.com/katipally/capybaraa && cd capybaraa
node test/smoke.js                 # the runnable checks (principles, parsing, skills)
claude --plugin-dir .              # load the plugin without installing
claude plugin validate .           # validate the manifest (Claude Code CLI)
```

To rerun the benchmark, you need the `claude` CLI and Python 3. From `benchmarks/agentic/`:

```bash
python3 run.py --selftest                            # prove every scorer offline, spends nothing
python3 run.py --task feat-rating,feat-export,feat-palette --arms baseline,caveman,ponytail,capybaraa --models sonnet --runs 2
python3 judge.py --complete-run runs/<stamp>         # completeness of the build tasks
python3 chart.py runs/<stamp> ../../assets/benchmark.svg
```

`--selftest` runs first on purpose: every gate ships a good and a bad reference and must pass the good and catch the bad before a single API call. ponytail must be installed (or `PONYTAIL_PLUGIN_DIR` set); caveman ships vendored, no install needed. Full method and isolation guarantees are in [`benchmarks/agentic/`](benchmarks/agentic/).

## Uninstall

`/plugin remove capybaraa`

## FAQ

**Does it slow every task down with questions?**
No. Trivial asks get the answer and nothing else. The questions only fire when the spec is ambiguous enough that guessing would build the wrong thing.

**Does it actually save tokens?**
It saves *code*: ~20% fewer lines than a bare agent, fully complete and fully safe (see the numbers). On *output tokens and cost* it depends on the model and task size. On small Haiku tasks it runs above baseline (+9% tokens, +13% cost): the always-on ruleset is re-read each turn and a tiny task can't amortize it. On the larger Sonnet run output tokens came in under baseline (90%). We don't claim a blanket token win; we claim less code, kept complete and safe.

**How is this different from ponytail?**
ponytail is tight, focused, and the leanest on raw lines. capybaraa is ponytail's discipline plus five habits: ask with an ASCII sketch, optimal code, terse output, clean refactors, and a real sync after a change. If you want pure ruthless leanness, use ponytail.

**Why a capybaraa?**
Calmest animal alive, gets along with everything, wastes zero energy. You already knew.

## Credit

Capybaraa owes a real debt to [**ponytail**](https://github.com/DietrichGebert/ponytail) by [Dietrich Gebert](https://github.com/DietrichGebert). The lazy-senior-dev idea, the lean ladder (does it need to exist, reuse, stdlib, native, one line), the always-on-via-hooks design, the review/audit command family, the four-arm benchmark shape (including the caveman control, vendored MIT), and the before/after-then-numbers shape of this README all trace back to it. Ponytail is the pure-minimal version; capybaraa keeps its lean discipline and adds a handful of habits (ask, optimal, terse, clean, sync). If you want the pure, ruthless leanness version, or just want to thank the original, [go star ponytail](https://github.com/DietrichGebert/ponytail).

## License

[MIT](LICENSE).
