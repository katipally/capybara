// Smallest checks that fail if the core logic breaks. `node test/smoke.js`.
'use strict';

const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');

const { getInstructions, normalizeState } = require('../principles/build-instructions.js');
const { parseCommand, isDeactivation, isActivation, writeHookOutput } = require('../hooks/config.js');

// principles: one always-on mode, no lean/deep delta
assert.strictEqual(getInstructions('off'), '', 'off => empty');
assert.match(getInstructions('on'), /CAPYBARAA ACTIVE/, 'on => instructions ship');
assert.doesNotMatch(getInstructions('on'), /mode:/i, 'no mode line ships anymore');
assert.doesNotMatch(getInstructions('on'), /MODE (lean|deep)/, 'no per-mode delta ships');
assert.match(getInstructions('on'), /2\. LEAN/, 'all seven pillars ship');
assert.match(getInstructions('on'), /7\. SYNC/, 'the sync pillar ships');
assert.match(getInstructions('on'), /7 pillars/, 'CORE announces seven pillars');
assert.match(getInstructions('on'), /CONSCIOUS GATE/, 'the conscious gate ships');
assert.match(getInstructions('on'), /references\/principles\.md/, 'CORE points at the detailed reference');
assert.match(getInstructions('on'), /🦫 capybaraa/, 'visible signal badge ships');
assert.doesNotMatch(getInstructions('on'), /🦫 capybaraa ·/, 'badge has no mode suffix');
assert.match(getInstructions('on'), /capybaraa:/, 'debt-marker convention ships in CORE');
assert.match(getInstructions('on'), /capybaraa-sync/, 'the sync reflex ships in CORE');

// state normalization: legacy mode values count as on, only "off" is off
assert.strictEqual(normalizeState('off'), 'off');
assert.strictEqual(normalizeState('on'), 'on');
assert.strictEqual(normalizeState('deep'), 'on', 'legacy deep => on');
assert.strictEqual(normalizeState('lean'), 'on', 'legacy lean => on');
assert.strictEqual(normalizeState('medium'), 'on', 'legacy medium => on');
assert.strictEqual(normalizeState(''), null, 'blank => no opinion (fall through)');
assert.strictEqual(getInstructions('deep'), getInstructions('on'), 'legacy value injects the same text');
assert.strictEqual(getInstructions('bogus'), getInstructions('on'), 'unknown value => on');

// command parsing: whole-message only (the substring-deactivation bug must stay fixed)
assert.strictEqual(parseCommand('/capybaraa on'), 'on');
assert.strictEqual(parseCommand('capybaraa off'), 'off');
assert.strictEqual(parseCommand('/capybaraa:capybaraa off'), 'off', 'namespaced form');
assert.strictEqual(parseCommand('please /capybaraa on now and then build it'), null, 'command buried in prose does NOT fire');
assert.strictEqual(parseCommand('no command here'), null);
assert.strictEqual(parseCommand('/capybaraa lean'), null, 'lean/deep are no longer commands');

assert.ok(isDeactivation('stop capybaraa'), 'bare deactivation fires');
assert.ok(isDeactivation('normal mode'), 'bare normal mode fires');
assert.ok(!isDeactivation('here is a doc that says stop capybaraa inline'), 'quoted phrase mid-message does NOT deactivate');
assert.ok(!isDeactivation('switch back to normal mode of operation later'), 'normal mode in prose does NOT deactivate');
assert.ok(isActivation('start capybaraa'));
assert.ok(isActivation('capybaraa on'));
assert.ok(!isActivation('we should capybaraa on the next sprint maybe'), 'activation in prose does NOT fire');

// the slash skills exist (Claude Code surfaces skills, not commands/*.toml)
for (const s of ['capybaraa', 'capybaraa-help', 'capybaraa-review', 'capybaraa-audit', 'capybaraa-sync', 'capybaraa-debt']) {
  const p = path.join(__dirname, '..', 'skills', s, 'SKILL.md');
  assert.ok(fs.existsSync(p), `missing skill ${s}`);
  assert.ok(fs.readFileSync(p, 'utf8').startsWith('---'), `skill ${s} needs frontmatter`);
}

// the detailed reference exists and names all seven pillars
const ref = fs.readFileSync(path.join(__dirname, '..', 'references', 'principles.md'), 'utf8');
for (const pillar of ['CLARIFY', 'LEAN', 'OPTIMAL', 'ECONOMY', 'COMPLETE', 'HYGIENE', 'SYNC']) {
  assert.match(ref, new RegExp(`## ${pillar}`), `reference missing ${pillar}`);
}
assert.match(ref, /conscious gate/i, 'reference documents the conscious gate');

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
