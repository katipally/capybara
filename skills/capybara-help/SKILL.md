---
name: capybara-help
description: Quick reference for capybara, what it does, the six pillars, and how to set the level. Use when the user types /capybara-help or asks how capybara works.
disable-model-invocation: true
license: MIT
---

# Capybara Help

Render this card, change nothing.

```
 capybara: calm senior-dev mode.
 the six pillars are ALWAYS ON; they apply to every task. no command needed.

 PILLARS  CLARIFY  explore first, then plan mode: curated questions + ASCII
                   on the options + edge cases, before non-trivial code
          LEAN     YAGNI · reuse · stdlib first
          OPTIMAL  right data structure · best feasible complexity
          ECONOMY  terse · no useless comments · minimal tokens
          COMPLETE root-cause fix · run the check before claiming done
          HYGIENE  replace not pile-on · kill dead code/stale comments ·
                   sanitize · flag security

 SLASH    /capybara [low|medium|high|off]   set intensity
          /capybara-review                  review a diff against the pillars
          /capybara-help                    this card

 LEVELS   low = nudges · medium = default · high = aggressive
 OFF      "stop capybara"  or  /capybara off
 DEFAULT  CAPYBARA_DEFAULT_LEVEL env (low|medium|high|off), or
          ~/.config/capybara/config.json {"defaultLevel":"high"}
```
