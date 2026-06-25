// Smallest checks that fail if the core logic breaks. `node test/smoke.js`.
'use strict';

const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');

const { getInstructions } = require('../principles/build-instructions.js');
const { parseCommand, isDeactivation, writeHookOutput } = require('../hooks/config.js');

// principles
assert.strictEqual(getInstructions('off'), '', 'off => empty');
assert.match(getInstructions('deep'), /mode: deep/);
assert.match(getInstructions('lean'), /mode: lean/);
assert.match(getInstructions('bogus'), /mode: deep/, 'unknown mode => default deep');
assert.match(getInstructions('deep'), /2\. LEAN/, 'all six pillars ship');
assert.match(getInstructions('deep'), /MODE deep/, 'deep delta ships');
assert.match(getInstructions('lean'), /MODE lean/, 'lean delta ships');
assert.doesNotMatch(getInstructions('deep'), /drop into plan mode/i, 'plan-mode wording reframed to behavior');
assert.match(getInstructions('deep'), /references\/principles\.md/, 'CORE points at the detailed reference');
assert.match(getInstructions('deep'), /🦫 capybaraa ·/, 'visible signal badge ships');
assert.match(getInstructions('lean'), /SIGNAL:/, 'signal is level-agnostic (ships in lean too)');

// command parsing
assert.strictEqual(parseCommand('please /capybaraa lean'), 'lean');
assert.strictEqual(parseCommand('use /capybaraa deep now'), 'deep');
assert.strictEqual(parseCommand('capybaraa off'), 'off');
assert.strictEqual(parseCommand('no command here'), null);
assert.ok(isDeactivation('stop capybaraa'));
assert.ok(isDeactivation('go normal mode now'));
assert.ok(!isDeactivation('keep going'));

// command parsing handles the namespaced form too
assert.strictEqual(parseCommand('/capybaraa:capybaraa off'), 'off');

// the slash skills exist (Claude Code surfaces skills, not commands/*.toml)
for (const s of ['capybaraa', 'capybaraa-help', 'capybaraa-review', 'capybaraa-audit']) {
  const p = path.join(__dirname, '..', 'skills', s, 'SKILL.md');
  assert.ok(fs.existsSync(p), `missing skill ${s}`);
  assert.ok(fs.readFileSync(p, 'utf8').startsWith('---'), `skill ${s} needs frontmatter`);
}

// the detailed reference exists and names all six pillars
const ref = fs.readFileSync(path.join(__dirname, '..', 'references', 'principles.md'), 'utf8');
for (const pillar of ['CLARIFY', 'LEAN', 'OPTIMAL', 'ECONOMY', 'COMPLETE', 'HYGIENE']) {
  assert.match(ref, new RegExp(`## ${pillar}`), `reference missing ${pillar}`);
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

console.log('ok: all smoke checks passed');
