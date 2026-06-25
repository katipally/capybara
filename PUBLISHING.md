# Publishing runbook

Three independent channels. Do them in any order; each needs *your* accounts.

```
 1. GitHub  → makes the Claude Code plugin installable from your repo  (done by push)
 2. npm     → makes `npx @katipally/capybara` work for everyone        (GitHub Action)
 3. Catalog → lists you in the official Claude Code marketplace        (optional)
```

## 1. GitHub (already pushed)

The repo is public at `https://github.com/katipally/capybara`, so Claude Code
users can already install straight from it, no approval needed:

```
/plugin marketplace add katipally/capybara
/plugin install capybara@capybara
```

When you change anything, commit and push to `main`. The marketplace pin follows
`ref: "main"` in `.claude-plugin/marketplace.json`.

## 2. npm (via GitHub Actions, OIDC, no secrets)

One-time setup:

1. Create the package owner on npm: `npm login`, then a first manual publish is
   **not** required. OIDC can do the very first publish too, but npm must know the
   package name belongs to you. Easiest path: `npm publish --access public` once
   from your machine to claim `@katipally/capybara`, **or** create the package via
   the npm website.
2. On npm: **@katipally/capybara → Settings → Trusted Publisher → Add GitHub
   Actions**, repo `katipally/capybara`, workflow `publish.yml`.

Every release after that:

```bash
# bump version in package.json + CHANGELOG.md, commit, then:
git tag v0.1.0
git push origin v0.1.0      # publish.yml runs: npm test → npm publish --provenance
```

The Action mints a short-lived token via OIDC, there is no `NPM_TOKEN` to manage.
Needs npm >= 11.5.1 (Node 22 in the workflow provides it).

## 3. Official Claude Code marketplace (optional)

Listing in the community catalog gets you discovery, not new capability. Direct
repo install already works.

1. Validate first (the review pipeline runs the same check):
   ```bash
   claude plugin validate .
   claude plugin validate . --strict
   ```
2. Submit:
   - Individual authors → <https://platform.claude.com/plugins/submit>
   - Org owners → <https://claude.ai/admin-settings/directory/submissions/plugins/new>
3. Automated safety screening runs; approved plugins are pinned to a commit SHA in
   `anthropics/claude-plugins-community` and synced nightly. Allow ~1-2 days.

Note: the npm package name is scoped (`@katipally/capybara`) because plain
`capybara` was taken. If you'd rather have a short unscoped `npx capybara-cc`,
rename `name` in `package.json` and the `npx` lines in the README before step 2.
