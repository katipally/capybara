// Level state + command parsing. Flag file is the source of truth for "current level".
'use strict';

const fs = require('fs');
const os = require('os');
const path = require('path');

const { VALID_LEVELS, DEFAULT_LEVEL } = require('../principles/build-instructions.js');

function configDir() {
  return process.env.CLAUDE_CONFIG_DIR || path.join(os.homedir(), '.claude');
}
function flagPath() {
  return path.join(configDir(), '.capybara-active');
}

function getLevel() {
  try {
    const v = fs.readFileSync(flagPath(), 'utf8').trim().toLowerCase();
    if (VALID_LEVELS.includes(v)) return v;
  } catch {}
  const env = (process.env.CAPYBARA_DEFAULT_LEVEL || '').trim().toLowerCase();
  if (VALID_LEVELS.includes(env)) return env;
  try {
    const cfg = path.join(os.homedir(), '.config', 'capybara', 'config.json');
    const v = JSON.parse(fs.readFileSync(cfg, 'utf8')).defaultLevel;
    if (VALID_LEVELS.includes(v)) return v;
  } catch {}
  return DEFAULT_LEVEL;
}

function setLevel(level) {
  try {
    fs.mkdirSync(configDir(), { recursive: true });
    fs.writeFileSync(flagPath(), `${level}\n`);
  } catch {}
}

// "/capybara high", "capybara low", "/capybara:capybara off" -> level; null if none.
function parseCommand(text) {
  const m = /(?:^|\s)[/@$]?capybara(?::capybara)?\s+(off|low|medium|high)\b/i.exec(text || '');
  return m ? m[1].toLowerCase() : null;
}
// "stop capybara" / "normal mode" -> deactivate.
function isDeactivation(text) {
  return /\b(stop\s+capybara|normal\s+mode)\b/i.test(text || '');
}

// Emit hook context in the form Claude Code expects per event.
// SessionStart / UserPromptSubmit accept raw stdout; SubagentStart DROPS raw text
// and requires the hookSpecificOutput JSON wrapper or the context never arrives.
function writeHookOutput(event, context) {
  if (!context) return;
  if (event === 'SubagentStart') {
    process.stdout.write(JSON.stringify({
      hookSpecificOutput: { hookEventName: event, additionalContext: context },
    }));
  } else {
    process.stdout.write(context);
  }
}

module.exports = { configDir, flagPath, getLevel, setLevel, parseCommand, isDeactivation, writeHookOutput };
