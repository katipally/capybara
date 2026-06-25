// Two prompt variants promptfoo runs head to head: the bare task (baseline) and the
// same task with capybara's principles prepended. The capybara text comes straight
// from the plugin's single source of truth, so the benchmark tests what ships.
'use strict';

const { getInstructions } = require('../principles/build-instructions.js');

function baseline({ vars }) {
  return vars.instruction;
}

function capybara({ vars }) {
  return `${getInstructions('high')}\n\n---\n\n${vars.instruction}`;
}

module.exports = { baseline, capybara };
