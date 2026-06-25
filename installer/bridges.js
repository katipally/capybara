// Per-platform bridges. One table, not four files. Each bridge detects its tool
// and writes the capybara principles into that tool's conventional rules file.
'use strict';

const fs = require('fs');
const os = require('os');
const path = require('path');
const { getInstructions } = require('../principles/build-instructions.js');

const HOME = os.homedir();
const exists = (p) => { try { return fs.existsSync(p); } catch { return false; } };

// Every bridge carries the full principle text at the default level.
const TEXT = () => getInstructions('medium');

const START = '<!-- capybara:start -->';
const END = '<!-- capybara:end -->';

// Write/refresh a delimited block so update is idempotent and uninstall is clean.
function writeBlock(file, body) {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  const block = `${START}\n${body}\n${END}`;
  let cur = exists(file) ? fs.readFileSync(file, 'utf8') : '';
  if (cur.includes(START) && cur.includes(END)) {
    cur = cur.replace(new RegExp(`${START}[\\s\\S]*${END}`), block);
  } else {
    cur = cur ? `${cur.trimEnd()}\n\n${block}\n` : `${block}\n`;
  }
  fs.writeFileSync(file, cur);
  return file;
}

function removeBlock(file) {
  if (!exists(file)) return null;
  let cur = fs.readFileSync(file, 'utf8');
  if (!cur.includes(START)) return null;
  cur = cur.replace(new RegExp(`\\n*${START}[\\s\\S]*${END}\\n*`), '\n').trim();
  if (cur) fs.writeFileSync(file, cur + '\n'); else fs.unlinkSync(file);
  return file;
}

// Cursor uses a dedicated .mdc rule file with its own frontmatter, own it whole.
function writeMdc(file) {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  const content = `---\ndescription: Capybara, calm senior-dev coding principles\nalwaysApply: true\n---\n\n${TEXT()}\n`;
  fs.writeFileSync(file, content);
  return file;
}

const BRIDGES = [
  {
    id: 'claude-code', name: 'Claude Code',
    detect: () => exists(path.join(HOME, '.claude')),
    target: (root) => path.join(root, 'CLAUDE.md'),
    install: (root) => writeBlock(path.join(root, 'CLAUDE.md'), TEXT()),
    remove: (root) => removeBlock(path.join(root, 'CLAUDE.md')),
    note: 'for full integration prefer the plugin: /plugin install capybara@capybara',
  },
  {
    id: 'cursor', name: 'Cursor',
    detect: () => exists(path.join(HOME, '.cursor')),
    target: (root) => path.join(root, '.cursor', 'rules', 'capybara.mdc'),
    install: (root) => writeMdc(path.join(root, '.cursor', 'rules', 'capybara.mdc')),
    remove: (root) => { const f = path.join(root, '.cursor', 'rules', 'capybara.mdc'); if (exists(f)) { fs.unlinkSync(f); return f; } return null; },
  },
  {
    id: 'copilot', name: 'GitHub Copilot',
    detect: () => exists(path.join(HOME, '.copilot')) || exists(path.join(HOME, '.config', 'copilot')),
    target: (root) => path.join(root, '.github', 'copilot-instructions.md'),
    install: (root) => writeBlock(path.join(root, '.github', 'copilot-instructions.md'), TEXT()),
    remove: (root) => removeBlock(path.join(root, '.github', 'copilot-instructions.md')),
  },
  {
    id: 'opencode', name: 'OpenCode',
    detect: () => exists(path.join(HOME, '.config', 'opencode')),
    target: (root) => path.join(root, 'AGENTS.md'),
    install: (root) => writeBlock(path.join(root, 'AGENTS.md'), TEXT()),
    remove: (root) => removeBlock(path.join(root, 'AGENTS.md')),
  },
];

function hasBlock(file) {
  return exists(file) && fs.readFileSync(file, 'utf8').includes(START);
}

module.exports = { BRIDGES, hasBlock, exists };
