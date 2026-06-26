---
name: capybaraa-help
description: Quick reference for capybaraa, what it does, the lean ladder and five habits, and how to turn it on or off. Use when the user types /capybaraa-help or asks how capybaraa works.
disable-model-invocation: true
license: MIT
---

# Capybaraa Help

Render this card, change nothing.

```
 capybaraa: lean senior-dev mode. ponytail's discipline + five habits.
 one mode, always on, scaled to the task. no command needed.

 LADDER   does it need to exist? · reuse what's here · stdlib/platform ·
          installed dep · one line · then the least code that works

 HABITS   ASK      Claude already asks; the add is an ASCII sketch on the
                   options when you do. ask only the deciding questions.
          OPTIMAL  right data structure · no needless O(n^2)
          TERSE    few words · few comments · no filler
          CLEAN    refactor = replace · kill dead code / stale comments
          SYNC     after a change, update docs/tests/refs/versions that
                   named the old shape · delete stale · /capybaraa-sync sweeps

 NEVER    drop validation, error handling, security, accessibility for fewer lines

 SLASH    /capybaraa [on|off]                turn it on or off
          /capybaraa-review                  review the diff against the rules
          /capybaraa-audit                   scan the whole repo for bloat + drift
          /capybaraa-sync                    fix drift: code vs its docs/tests/refs
          /capybaraa-help                    this card

 DETAIL   longer guidance: references/principles.md

 SIGNAL   replies open with  🦫  so you can see it is on. no other ceremony.
 OFF      "stop capybaraa"  or  /capybaraa off
 DEFAULT  CAPYBARAA_DEFAULT_LEVEL env (on|off), or
          ~/.config/capybaraa/config.json {"defaultState":"off"}
```
