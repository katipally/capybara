#!/usr/bin/env node
// capybara <init|doctor|update|uninstall|help>, run via `npx @katipally/capybara <cmd>`
// or `capybara <cmd>` once installed. Installs the principle bridges into
// whichever AI coding tools you have, in the current project.
'use strict';

const { stdout } = require('node:process');
const { BRIDGES, hasBlock, exists } = require('../installer/bridges.js');
const { runWizard } = require('../installer/wizard.js');

const c = (n, s) => `\x1b[${n}m${s}\x1b[0m`;
const root = process.cwd();

function doctor() {
  stdout.write(c('1', '\ncapybara doctor') + ` (project: ${root})\n\n`);
  for (const b of BRIDGES) {
    const f = b.target(root);
    const installed = b.id === 'cursor' ? exists(f) : hasBlock(f);
    const tool = b.detect() ? 'tool detected' : c('90', 'tool not detected');
    stdout.write(`  ${installed ? c('38;5;108', '✓ installed') : c('90', '· not installed')}  ${b.name}  (${tool})\n`);
  }
  stdout.write('\n');
}

function update() {
  stdout.write(c('1', '\ncapybara update') + '\n\n');
  let n = 0;
  for (const b of BRIDGES) {
    const f = b.target(root);
    const installed = b.id === 'cursor' ? exists(f) : hasBlock(f);
    if (installed) { b.install(root); stdout.write(c('38;5;108', '  ✓ ') + `${b.name} refreshed\n`); n++; }
  }
  stdout.write(n ? '\n' : c('90', '  nothing installed here yet, run "capybara init".\n\n'));
}

function uninstall() {
  stdout.write(c('1', '\ncapybara uninstall') + '\n\n');
  let n = 0;
  for (const b of BRIDGES) {
    const removed = b.remove(root);
    if (removed) { stdout.write(c('90', '  − ') + `${b.name} removed (${removed})\n`); n++; }
  }
  stdout.write(n ? '\n' : c('90', '  nothing to remove here.\n\n'));
}

function help() {
  stdout.write(`
🦫 ${c('1;38;5;179', 'capybara')}  calm senior-dev principles for AI coding agents

  ${c('1', 'capybara init')}       detect your tools and install the bridges (this project)
  ${c('1', 'capybara doctor')}     show what's installed where
  ${c('1', 'capybara update')}     refresh installed bridges to the latest text
  ${c('1', 'capybara uninstall')}  remove capybara from this project's tool files
  ${c('1', 'capybara help')}       this

Run via npx: ${c('1', 'npx @katipally/capybara init')}
Claude Code users: prefer the native plugin, /plugin install capybara@capybara
`);
}

const cmd = (process.argv[2] || 'help').toLowerCase();
({ init: () => runWizard(root), doctor, update, uninstall, help }[cmd] || help)();
