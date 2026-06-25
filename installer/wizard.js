// Interactive init wizard. Zero deps: node:readline/promises + raw ANSI.
'use strict';

const readline = require('node:readline/promises');
const { stdin, stdout } = require('node:process');
const { BRIDGES } = require('./bridges.js');

const c = (n, s) => `\x1b[${n}m${s}\x1b[0m`;

async function runWizard(root) {
  stdout.write(c('1;38;5;179', '\n🦫 capybara init') + '  installing principles into your tools\n\n');

  const detected = BRIDGES.map((b) => ({ b, on: b.detect() }));
  detected.forEach(({ b, on }, i) => {
    stdout.write(`  ${i + 1}. ${b.name} ${on ? c('38;5;108', '(detected)') : c('90', '(not detected)')}\n`);
  });

  const rl = readline.createInterface({ input: stdin, output: stdout });
  const def = detected.map(({ on }, i) => (on ? i + 1 : null)).filter(Boolean).join(',') || '1';
  const ans = (await rl.question(`\nInstall which? numbers comma-separated, or "all" [${def}]: `)).trim();
  rl.close();

  let pick;
  if (!ans) pick = def.split(',').map(Number);
  else if (/^all$/i.test(ans)) pick = BRIDGES.map((_, i) => i + 1);
  else pick = ans.split(',').map((s) => parseInt(s, 10)).filter((n) => n >= 1 && n <= BRIDGES.length);

  if (!pick.length) { stdout.write(c('90', 'Nothing selected. Bye.\n')); return; }

  stdout.write('\n');
  for (const n of pick) {
    const b = BRIDGES[n - 1];
    try {
      const f = b.install(root);
      stdout.write(c('38;5;108', '  ✓ ') + `${b.name} → ${f}\n`);
      if (b.note) stdout.write(c('90', `      ${b.note}\n`));
    } catch (e) {
      stdout.write(c('38;5;203', '  ✗ ') + `${b.name}: ${e.message}\n`);
    }
  }
  stdout.write(c('90', '\nRun "capybara doctor" to verify, "capybara update" to refresh.\n'));
}

module.exports = { runWizard };
