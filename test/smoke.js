// Smallest checks that fail if the core logic breaks. `node test/smoke.js`.
'use strict';

const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');

const { getInstructions, normalizeState } = require('../principles/build-instructions.js');
const { parseCommand, isDeactivation, isActivation, writeHookOutput } = require('../hooks/config.js');

// principles: one always-on mode, lean ladder + five habits, no verbose framing
const onText = getInstructions('on');
assert.strictEqual(getInstructions('off'), '', 'off => empty');
assert.match(onText, /CAPYBARAA ACTIVE/, 'on => instructions ship');
assert.doesNotMatch(onText, /mode:/i, 'no mode line ships anymore');
assert.doesNotMatch(onText, /MODE (lean|deep)/, 'no per-mode delta ships');
assert.match(onText, /The ladder/, 'the lean ladder ships');
for (const habit of ['ASK', 'OPTIMAL', 'TERSE', 'CLEAN', 'SYNC']) {
  assert.match(onText, new RegExp(`\\b${habit}\\b`), `the ${habit} habit ships`);
}
assert.match(onText, /ASCII diagram/, 'the ASCII-on-questions rule ships in CORE');
assert.match(onText, /🦫/, 'visible signal badge ships');
// the old wall of text is gone: that is the whole point of the lean rewrite
assert.doesNotMatch(onText, /7 pillars|seven pillars/, 'no seven-pillar framing');
assert.doesNotMatch(onText, /CONSCIOUS GATE/, 'no conscious-gate essay');
assert.doesNotMatch(onText, /sign-off/, 'no sign-off ceremony');
assert.ok(onText.length < 2500, `CORE stays lean (was ${onText.length} chars)`);

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
for (const s of ['capybaraa', 'capybaraa-help', 'capybaraa-review', 'capybaraa-audit', 'capybaraa-sync']) {
  const p = path.join(__dirname, '..', 'skills', s, 'SKILL.md');
  assert.ok(fs.existsSync(p), `missing skill ${s}`);
  assert.ok(fs.readFileSync(p, 'utf8').startsWith('---'), `skill ${s} needs frontmatter`);
}
assert.ok(!fs.existsSync(path.join(__dirname, '..', 'skills', 'capybaraa-debt', 'SKILL.md')), 'capybaraa-debt skill removed');

// the detailed reference exists and names the lean ladder + the five habits
const ref = fs.readFileSync(path.join(__dirname, '..', 'references', 'principles.md'), 'utf8');
for (const rule of ['LEAN', 'ASK', 'OPTIMAL', 'TERSE', 'CLEAN', 'SYNC']) {
  assert.match(ref, new RegExp(`## .*${rule}`), `reference missing ${rule}`);
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
