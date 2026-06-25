# Contributing

Thanks for helping keep the swamp calm.

## Setup

```bash
git clone https://github.com/katipally/capybara && cd capybara
node test/smoke.js          # no dependencies to install, stdlib only
```

## Before a PR

```bash
node test/smoke.js          # must pass
claude plugin validate .    # if you have the Claude Code CLI
```

## Ground rules (capybara eats its own cooking)

- **Single source of truth.** The principle text lives once in
  `principles/build-instructions.js`. Don't copy it into bridges or skills,
  consume it.
- **Zero runtime deps.** The installer uses Node >=18 built-ins only. Don't add a
  package for what a few lines of stdlib do.
- **Leave a check.** Non-trivial logic gets one assertion in `test/smoke.js`.
- **No dead code.** If you replace something, delete the old version.

Keep diffs small. Boring over clever.
