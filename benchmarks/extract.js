// Pull the code out of a model answer and turn a `function` task's code into a
// callable. Kept deliberately small: grab the first fenced block if present,
// otherwise use the whole answer, then build the named function from it.
'use strict';

function extractCode(answer) {
  const fence = /```(?:js|javascript)?\s*([\s\S]*?)```/i.exec(answer || '');
  return (fence ? fence[1] : answer || '').trim();
}

// Build and return the function named `name` from the answer's code.
// Supports `function name(...)`, `const name = ...`, and arrow forms.
function buildFunction(answer, name) {
  const code = extractCode(answer);
  // eslint-disable-next-line no-new-func
  const factory = new Function(`${code}\n; return typeof ${name} === 'function' ? ${name} : undefined;`);
  return factory();
}

module.exports = { extractCode, buildFunction };
