#!/usr/bin/env node
// Summarize a promptfoo run into a capybara-vs-baseline table: median lines of code,
// pass rate, median cost, median latency, and the capybara reduction.
//
//   node score.js results/latest.json
'use strict';

const fs = require('fs');

const file = process.argv[2] || 'results/latest.json';
let data;
try {
  data = JSON.parse(fs.readFileSync(file, 'utf8'));
} catch (e) {
  console.error(`can't read ${file}: ${e.message}`);
  console.error('run the eval first: npx promptfoo eval -c promptfooconfig.yaml --output results/latest.json');
  process.exit(1);
}

// promptfoo nests results differently across versions; normalize to a flat array.
const rows = data?.results?.results || data?.results || (Array.isArray(data) ? data : []);
if (!rows.length) {
  console.error('no result rows found in the output file');
  process.exit(1);
}

const median = (xs) => {
  const a = xs.filter((x) => typeof x === 'number' && !Number.isNaN(x)).sort((p, q) => p - q);
  if (!a.length) return null;
  const m = Math.floor(a.length / 2);
  return a.length % 2 ? a[m] : (a[m - 1] + a[m]) / 2;
};

const groups = new Map(); // label -> { loc:[], cost:[], lat:[], pass:0, n:0 }
for (const r of rows) {
  const label = r?.prompt?.label || r?.promptLabel || 'unknown';
  const g = groups.get(label) || { loc: [], cost: [], lat: [], pass: 0, n: 0 };
  g.loc.push(r?.namedScores?.loc);
  g.cost.push(r?.response?.cost ?? r?.cost);
  g.lat.push(r?.latencyMs ?? r?.response?.latencyMs);
  if (r?.success) g.pass += 1;
  g.n += 1;
  groups.set(label, g);
}

const fmt = (x, d = 2) => (x == null ? '  -  ' : x.toFixed(d));
console.log('\ncapybara benchmark  (medians across all tasks, providers, repeats)\n');
console.log('variant    runs  pass%   loc   cost($)   latency(ms)');
console.log('-------------------------------------------------------');
const sum = {};
for (const [label, g] of groups) {
  const s = { loc: median(g.loc), cost: median(g.cost), lat: median(g.lat), passPct: (g.pass / g.n) * 100, n: g.n };
  sum[label] = s;
  console.log(
    `${label.padEnd(10)} ${String(g.n).padStart(4)}  ${fmt(s.passPct, 0).padStart(4)}  ${fmt(s.loc, 0).padStart(5)}  ${fmt(s.cost, 4).padStart(8)}  ${fmt(s.lat, 0).padStart(10)}`,
  );
}

if (sum.baseline && sum.capybara) {
  const drop = (a, b) => (a && b ? `${(((a - b) / a) * 100).toFixed(0)}%` : '-');
  console.log('\ncapybara vs baseline:');
  console.log(`  lines    ${drop(sum.baseline.loc, sum.capybara.loc)} fewer`);
  console.log(`  cost     ${drop(sum.baseline.cost, sum.capybara.cost)} cheaper`);
  console.log(`  latency  ${drop(sum.baseline.lat, sum.capybara.lat)} faster`);
  console.log(`  safety   baseline ${sum.baseline.passPct.toFixed(0)}% correct, capybara ${sum.capybara.passPct.toFixed(0)}% correct`);
}
console.log('');
