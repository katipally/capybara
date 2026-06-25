#!/usr/bin/env node
// UserPromptSubmit: catch "/capybara <level>" and "stop capybara" to switch state.
'use strict';

const { parseCommand, isDeactivation, setLevel, writeHookOutput } = require('./config.js');

let input = '';
process.stdin.on('data', (c) => (input += c));
process.stdin.on('end', () => {
  let prompt = '';
  try { prompt = JSON.parse(input).prompt || ''; } catch { prompt = input; }

  if (isDeactivation(prompt)) {
    setLevel('off');
    writeHookOutput('UserPromptSubmit', '[capybara] off. Say "capybara medium" to re-enable.');
  } else {
    const lvl = parseCommand(prompt);
    if (lvl) {
      setLevel(lvl);
      writeHookOutput('UserPromptSubmit', lvl === 'off' ? '[capybara] off.' : `[capybara] level: ${lvl}.`);
    }
  }
  process.exit(0);
});
