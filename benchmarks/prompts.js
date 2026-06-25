// Two prompt variants promptfoo runs head to head: the bare task (baseline) and the
// same task with capybaraa's principles prepended. The capybaraa text comes straight
// from the plugin's single source of truth, so the benchmark tests what ships.
'use strict';

const { getInstructions } = require('../principles/build-instructions.js');

function baseline({ vars }) {
  return vars.instruction;
}

function capybaraa({ vars }) {
  return `${getInstructions('deep')}\n\n---\n\n${vars.instruction}`;
}

module.exports = { baseline, capybaraa };
