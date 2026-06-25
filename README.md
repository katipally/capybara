<h1 align="center">🦫 Capybara</h1>

<p align="center">
  <em>The chillest senior dev in the swamp. Doesn't panic. Doesn't over-build. Asks first, ships clean, leaves.</em>
</p>

<p align="center">
  <img src="https://img.shields.io/npm/v/@katipally/capybara?style=flat-square&color=8a6d3b&label=npm" alt="npm">
  <img src="https://img.shields.io/badge/works%20with-4%20tools-8a6d3b?style=flat-square" alt="Works with 4 tools">
  <img src="https://img.shields.io/badge/license-MIT-8a6d3b?style=flat-square" alt="MIT license">
  <img src="https://img.shields.io/badge/levels-low%20·%20medium%20·%20high-8a6d3b?style=flat-square" alt="Levels">
</p>

---

You know the type. Unbothered. Has seen every framework rise and fall and didn't migrate to any of them. You hand over a vague ticket and fifty lines of someone's first draft; he reads it, asks the two questions that actually matter, draws a little box-and-arrow on a napkin, and replaces the whole thing with the part you needed.

Capybara puts him inside your AI agent.

It's the half of "good engineering" that AI agents skip: **think before you type, then leave the place clean.** Ponytail already nails *write less code* — capybara is broader. It makes the agent clarify the spec, pick the right complexity, stop padding output, actually verify "done," and not leave dead code and stale comments behind.

## Before / after

You ask for "add a settings page." Your agent invents a `SettingsManager`, a `ConfigProvider`, three new files, a migration, and starts coding before it knows what settings you even mean.

With capybara:

```
🦫 a couple of questions first:

   ┌─ settings ─┐
   │ theme      │  ← persisted where? (localStorage / your API / both)
   │ ...        │
   └────────────┘

   1. Just theme for now, or more fields coming?
   2. Per-device or synced to the account?

   edge cases I'll handle: no-JS fallback, unknown stored value, first load.
```

Then it writes the smallest thing that answers your actual answers — and runs the check before saying it's done.

## The six pillars

> **The capybara way:** understand the prompt → gather real context → learn the
> codebase → research & explore → *then* ask curated questions (with ASCII) → propose
> the best, future-proof option → implement the real root-cause fix. **Never patchwork.**

| Pillar | What it enforces |
|--------|------------------|
| **CLARIFY** | Understand and explore *first*, then ask — as many curated questions as the requirement actually needs (one or a dozen, never a fixed quota), an ASCII sketch in nearly every one, explicit edge cases. Don't guess the spec. |
| **LEAN** | YAGNI ladder — does it need to exist? reuse what's here? stdlib? native? one line? *then* minimal code. |
| **OPTIMAL** | Right data structure, best feasible time/space, no needless O(n²). |
| **ECONOMY** | Terse output, no useless comments or filler, minimal tokens, no over-exploring. |
| **COMPLETE** | Finish terminally, root cause not symptom, and **run the check** before claiming done. |
| **HYGIENE** | Refactor = replace, not pile-on; delete dead code & stale comments; sanitize inputs; flag security — out-of-scope finds get surfaced, not silently changed. |

The point was never "fewest tokens." It's: do exactly what the task needs, understand it first, and never cut validation, error handling, security, or accessibility. The code ends up small because it's *necessary*, not golfed.

## How it works

One source of truth — [`principles/build-instructions.js`](principles/build-instructions.js) — injected every session by a `SessionStart` hook and into every subagent by a `SubagentStart` hook. Your level lives in a flag file (`~/.claude/.capybara-active`).

It's **proportional**, on purpose:

```
 ALWAYS-ON  (cheap)    the 6 pillars as terse rules. prompt-cached → ~free per turn.
 ON-DEMAND  (earns it) full clarify-planning + the run-the-tests done-gate fire only
                       when the task is big enough to deserve them.
```

A one-line fix gets the rules and nothing else — no ceremony, no token burst. A real feature gets the full treatment.

## Install

### Claude Code (native plugin — recommended)

```
/plugin marketplace add katipally/capybara
```
```
/plugin install capybara@capybara
```
(Two separate prompts.) Needs `node` on your PATH for the lifecycle hooks; without it the skills still work, the always-on activation just stays quiet.

### Cursor · Copilot · OpenCode (one-shot wizard)

Run in your project — it detects what you have and writes each tool's rules file:

```bash
npx @katipally/capybara init       # detect tools, install the rules
npx @katipally/capybara doctor     # show what's installed where
npx @katipally/capybara update     # refresh to the latest text
```

(After `npm i -g @katipally/capybara`, it's just `capybara init`.)

## Levels

```
/capybara low | medium | high | off          "stop capybara" also turns it off
```

| `low` | nudges only — build it, name the leaner option in one line |
| `medium` *(default)* | all pillars, proportional; ASCII planning when warranted |
| `high` | aggressive — max questioning, deletion-first, strict done-gate |

The level shows in your statusline as `[CAPYBARA]` / `[CAPYBARA:HIGH]`. Set a default for every session with `CAPYBARA_DEFAULT_LEVEL` (`low`/`medium`/`high`/`off`) or `defaultLevel` in `~/.config/capybara/config.json`. Default is `medium`.

## Commands

| Command | What it does |
|---------|--------------|
| `/capybara [low \| medium \| high \| off]` | Set the intensity, or turn it off. No argument reports the current level. |
| `/capybara-plan` | Clarify before code: ASCII diagram, grouped questions, edge cases, minimal spec. |
| `/capybara-review` | Review the current diff against the six pillars — what to delete, optimize, clean. |
| `/capybara-clean` | Hygiene pass on what you touched: dead code, stale comments, sanitize, flag security. |
| `/capybara-done` | The done-gate: checklist + actually run the test/build before claiming done. |
| `/capybara-help` | Quick reference card. |

Commands need a skill-capable host (Claude Code). The wizard-installed tools (Cursor, Copilot, OpenCode) get the always-on rules without the slash commands.

## Develop & test locally

```bash
git clone https://github.com/katipally/capybara && cd capybara
node test/smoke.js                 # the runnable checks (principles, parsing, bridges)
claude --plugin-dir .              # load the plugin in Claude Code without installing
claude plugin validate .           # validate the manifest (Claude Code CLI)
```

To exercise the wizard without publishing: `node bin/capybara.js init` in a throwaway directory.

## Coexists with ponytail

If [ponytail](https://github.com/DietrichGebert/ponytail) is also active, capybara drops its overlapping **LEAN** pillar so you don't pay for the same "write less code" guidance twice — capybara then contributes the other five (clarify, optimal, economy, complete, hygiene) on top.

## Uninstall

| Host | Command |
|------|---------|
| Claude Code | `/plugin remove capybara` |
| Cursor / Copilot / OpenCode | `npx @katipally/capybara uninstall` (removes the rules it wrote) |

## FAQ

**Does it slow every task down with questions?**
No. Trivial asks get the rules and nothing else. Questions and the done-gate only fire when the task is big or ambiguous enough to need them.

**Funny name, but is the output professional?**
Yes. The branding is chill; the injected behavior is plain, senior, and reliable. No slang in your code.

**Do I need a config file?**
No. `CAPYBARA_DEFAULT_LEVEL` or `~/.config/capybara/config.json` can set a default level, but nothing is required.

**Why a capybara?**
Calmest animal alive, gets along with everything, wastes zero energy. You already knew.

## License

[MIT](LICENSE).
