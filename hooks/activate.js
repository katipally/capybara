#!/usr/bin/env node
// SessionStart: ensure flag exists, inject the mode-filtered principles, nudge statusline once.
'use strict';

const fs = require('fs');
const path = require('path');
const { getLevel, setLevel, flagPath, writeHookOutput } = require('./config.js');
const { getInstructions } = require('../principles/build-instructions.js');

const level = getLevel();
if (!fs.existsSync(flagPath())) setLevel(level); // first run: persist default

if (level !== 'off') {
  let out = getInstructions(level);

  // One-time statusline nudge: only if no statusline configured yet.
  try {
    const settings = path.join(process.env.CLAUDE_CONFIG_DIR || path.join(require('os').homedir(), '.claude'), 'settings.json');
    const raw = fs.existsSync(settings) ? JSON.parse(fs.readFileSync(settings, 'utf8')) : {};
    if (!raw.statusLine) {
      const sh = path.join(__dirname, 'statusline.sh');
      out += `\n\n[capybaraa] Optional: show the mode badge in your statusline by adding to settings.json:\n"statusLine": { "type": "command", "command": "bash \\"${sh}\\"" }`;
    }
  } catch {}

  writeHookOutput('SessionStart', out);
}
process.exit(0);
