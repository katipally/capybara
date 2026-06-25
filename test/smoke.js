// Smallest checks that fail if the core logic breaks. `node test/smoke.js`.
'use strict';

const assert = require('node:assert');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');

const { getInstructions } = require('../principles/build-instructions.js');
const { parseCommand, isDeactivation, writeHookOutput } = require('../hooks/config.js');
const { BRIDGES, hasBlock } = require('../installer/bridges.js');

// principles
assert.strictEqual(getInstructions('off'), '', 'off => empty');
assert.match(getInstructions('medium'), /level: medium/);
assert.match(getInstructions('bogus'), /level: medium/, 'unknown level => default');
assert.match(getInstructions('medium', true), /handled by ponytail/, 'ponytail dedupe drops LEAN');
assert.doesNotMatch(getInstructions('medium', false).match(/2\. LEAN[\s\S]*?3\. OPTIMAL/)[0], /handled by ponytail/);

// command parsing
assert.strictEqual(parseCommand('please /capybara high'), 'high');
assert.strictEqual(parseCommand('capybara off'), 'off');
assert.strictEqual(parseCommand('no command here'), null);
assert.ok(isDeactivation('stop capybara'));
assert.ok(isDeactivation('go normal mode now'));
assert.ok(!isDeactivation('keep going'));

// bridges install + idempotent update + doctor + remove, in a temp project
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'capy-'));
const claude = BRIDGES.find((b) => b.id === 'claude-code');
const f1 = claude.install(tmp);
assert.ok(hasBlock(f1), 'block written');
claude.install(tmp); // re-run
const once = fs.readFileSync(f1, 'utf8').match(/capybara:start/g).length;
assert.strictEqual(once, 1, 'update is idempotent (one block, not two)');
claude.remove(tmp);
assert.ok(!hasBlock(f1) && !fs.existsSync(f1), 'remove cleans up');
fs.rmSync(tmp, { recursive: true, force: true });

// command parsing handles the namespaced form too
assert.strictEqual(parseCommand('/capybara:capybara off'), 'off');

// the two slash commands exist (these ARE the plugin's only commands)
for (const c of ['capybara.toml', 'capybara-help.toml']) {
  assert.ok(fs.existsSync(path.join(__dirname, '..', 'commands', c)), `missing command ${c}`);
}

// SubagentStart MUST be JSON-wrapped or Claude Code drops the context
const captured = [];
const orig = process.stdout.write;
process.stdout.write = (s) => { captured.push(s); return true; };
writeHookOutput('SubagentStart', 'hello');
writeHookOutput('SessionStart', 'plain');
process.stdout.write = orig;
assert.deepStrictEqual(JSON.parse(captured[0]).hookSpecificOutput, { hookEventName: 'SubagentStart', additionalContext: 'hello' });
assert.strictEqual(captured[1], 'plain', 'SessionStart stays raw');

console.log('ok — all smoke checks passed');
