# Comparison Samples

## One-shot anti-pattern

`Fix all problems, make it secure, and keep trying.`

## Direct bounded task

`Change only parser.py to reject empty IDs; preserve the API; add two tests; run the focused suite; stop after pass or two failed attempts.`

## Planning request

`/plan Inspect the parser call graph, ask at most three contract questions, compare two designs, identify risks/tests, do not edit, and stop for design approval.`

## Execution contract

`/goal Implement approved option 2, milestone 1 only, with gpt-5.6-sol at the recorded effort. One smallest change per attempt, focused evidence after each, two attempts maximum, stop on scope or authority change. Compare gpt-6-astra only after the named attributed-failure trigger, with prompt, inputs, tools, permissions, and tests unchanged.`

## Evidence steer

`Steer: new trace shows decoding, not parsing. Keep scope and budget unchanged; revise the hypothesis and invalidate prior test evidence.`

## Side chat

`/side Explain the current failing-test hypothesis and remaining budget. Do not change the goal, files, or active acceptance criteria.`
