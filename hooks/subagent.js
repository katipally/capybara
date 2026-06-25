#!/usr/bin/env node
// SubagentStart: carry the principles into spawned subagents so they stay on-brand.
'use strict';

const { getLevel, writeHookOutput } = require('./config.js');
const { getInstructions } = require('../principles/build-instructions.js');

const level = getLevel();
if (level !== 'off') writeHookOutput('SubagentStart', getInstructions(level));
process.exit(0);
