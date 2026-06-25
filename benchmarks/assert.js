// promptfoo assertion: did the answer actually work? Looks up the task by id
// (passed in vars.taskId), runs its correctness check, and returns pass/fail.
// A short answer that doesn't work fails here, which is the whole point.
'use strict';

const { tasks } = require('./tasks.js');
const { buildFunction } = require('./extract.js');

module.exports = async (output, context) => {
  const taskId = context && context.vars && context.vars.taskId;
  const task = tasks.find((t) => t.id === taskId);
  if (!task) return { pass: false, score: 0, reason: `unknown task: ${taskId}` };

  try {
    if (task.kind === 'structural') {
      const ok = await task.check(output);
      return { pass: !!ok, score: ok ? 1 : 0, reason: ok ? 'structural check passed' : 'structural check failed' };
    }
    const fn = buildFunction(output, fnName(task));
    if (typeof fn !== 'function') return { pass: false, score: 0, reason: `no function ${fnName(task)} found` };
    const ok = await task.check(fn);
    return { pass: !!ok, score: ok ? 1 : 0, reason: ok ? 'correct' : 'wrong output' };
  } catch (e) {
    return { pass: false, score: 0, reason: `threw: ${e.message}` };
  }
};

// The instruction names the function in backticks, e.g. `isEmail(s)`.
function fnName(task) {
  const m = /`([A-Za-z_$][\w$]*)\s*\(/.exec(task.instruction);
  return m ? m[1] : task.id;
}
