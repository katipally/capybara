// Build one promptfoo test case per task. Each carries a correctness gate
// (assert.js) and a line-count metric (loc.js). promptfoo runs every test against
// every prompt variant and every provider in promptfooconfig.yaml.
'use strict';

const { tasks } = require('./tasks.js');

module.exports = tasks.map((t) => ({
  description: t.id,
  vars: { taskId: t.id, instruction: t.instruction },
  assert: [
    { type: 'javascript', value: 'file://assert.js' },
    { type: 'javascript', value: 'file://loc.js', metric: 'loc' },
  ],
}));
