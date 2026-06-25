# Releasing

capybaraa is a Claude Code plugin, distributed straight from this GitHub repo:
no npm, no registry. Users install it with `/plugin marketplace add
katipally/capybaraa`, and the marketplace pin follows `ref:"main"` in
`.claude-plugin/marketplace.json`. So **a release is just a push to `main`.**

```
 edit + bump versions  ──▶  push to main  ──▶  users on the marketplace pin get it
 (optional) git tag vX.Y.Z ──▶ push tag    ──▶  a GitHub Release for the changelog
```

## Cut a release

1. Bump the version in **both** manifests (keep them equal):
   - `.claude-plugin/plugin.json`
   - `.claude-plugin/marketplace.json` (the nested `plugins[0].version`)
2. Add a dated `## [X.Y.Z]` section to `CHANGELOG.md`.
3. Validate and test locally:
   ```bash
   npm test                 # node test/smoke.js
   claude plugin validate . # manifest check (Claude Code CLI)
   ```
4. Commit and push to `main`. Done. Marketplace users get it on their next pull.

CI (`.github/workflows/ci.yml`) runs `npm test` on Node 18/20/22 and a best-effort
manifest validation for every push and PR, so a broken plugin never lands on `main`.

## Optional: tag a GitHub Release

If you want a visible release entry with notes:

```bash
git tag vX.Y.Z
git push origin vX.Y.Z
gh release create vX.Y.Z --title vX.Y.Z --generate-notes
```

Tags are cosmetic here. They don't change what marketplace users receive (that's
driven by `ref:"main"`).

## Optional: official Claude Code marketplace

Listing in the community catalog adds discovery, not capability: direct repo
install already works. Validate, then submit:

```bash
claude plugin validate .
claude plugin validate . --strict
```

- Individual authors → <https://platform.claude.com/plugins/submit>
- Org owners → <https://claude.ai/admin-settings/directory/submissions/plugins/new>

Approved plugins are pinned to a commit SHA in `anthropics/claude-plugins-community`
and synced nightly. Allow 1 to 2 days.
