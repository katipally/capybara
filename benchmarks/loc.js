// promptfoo assertion that never fails: it just records the answer's line count as
// a score so we can compare capybara vs. baseline. Counts non-blank lines of the
// extracted code (or the whole answer for structural tasks).
'use strict';

const { extractCode } = require('./extract.js');

module.exports = (output) => {
  const code = extractCode(output);
  const loc = code.split('\n').filter((l) => l.trim() !== '').length;
  return { pass: true, score: loc, reason: `loc=${loc}` };
};
