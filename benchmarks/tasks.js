// The benchmark task list. Each task is an everyday coding ask plus a correctness
// check, so a short-but-broken answer fails instead of scoring well on line count.
//
// `check(fn)` receives the function the model produced (already extracted from its
// answer and built) and returns true only if it actually works. `structural` tasks
// have no executable function; their check reads the raw answer text instead.
'use strict';

const tasks = [
  {
    id: 'email-validator',
    kind: 'function',
    instruction:
      'Write a JavaScript function `isEmail(s)` that returns true for a valid email ' +
      'address and false otherwise. Return only the function.',
    check(isEmail) {
      return (
        isEmail('a@b.co') === true &&
        isEmail('x.y+z@sub.domain.com') === true &&
        isEmail('no-at-sign') === false &&
        isEmail('a@b') === false &&
        isEmail('') === false &&
        isEmail('a b@c.com') === false
      );
    },
  },
  {
    id: 'debounce',
    kind: 'function',
    instruction:
      'Write a JavaScript function `debounce(fn, ms)` returning a debounced version ' +
      'of fn that runs only after ms of quiet. Return only the function.',
    async check(debounce) {
      let calls = 0;
      const d = debounce(() => { calls += 1; }, 20);
      d(); d(); d();
      await new Promise((r) => setTimeout(r, 50));
      return calls === 1;
    },
  },
  {
    id: 'csv-column-sum',
    kind: 'function',
    instruction:
      'Write a JavaScript function `sumColumn(csv, name)` that parses a CSV string ' +
      'with a header row and returns the numeric sum of the named column. Return only the function.',
    check(sumColumn) {
      const csv = 'a,b,c\n1,2,3\n4,5,6';
      return sumColumn(csv, 'b') === 7 && sumColumn(csv, 'a') === 5;
    },
  },
  {
    id: 'flatten',
    kind: 'function',
    instruction:
      'Write a JavaScript function `flatten(arr)` that fully flattens an arbitrarily ' +
      'nested array of numbers into a flat array, in order. Return only the function.',
    check(flatten) {
      return JSON.stringify(flatten([1, [2, [3, [4]], 5]])) === JSON.stringify([1, 2, 3, 4, 5]);
    },
  },
  {
    // Over-build trap: the lean answer is a one-line native input, not a component.
    id: 'date-input',
    kind: 'structural',
    instruction:
      'I need a date field in a plain HTML form. Give me the markup.',
    check(answer) {
      const a = answer.toLowerCase();
      // pass if it reaches for the native input and does NOT pull a date-picker library
      const native = a.includes('type="date"') || a.includes("type='date'");
      const heavy = /flatpickr|datepicker|moment|react-datepicker|npm install|yarn add/.test(a);
      return native && !heavy;
    },
  },
];

module.exports = { tasks };
