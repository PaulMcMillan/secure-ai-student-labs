# Module 3 context-packet example

This dependency-free example evaluates a static task packet before agent execution. It does not call Codex, read credentials, or use the network. In the 2026-09 module it forms the first two states of the M03-D01 comparison; the shared `examples/rag-reference` adds the functional retrieval-grounded state.

## Scenario

A synthetic pricing repository needs an approved bulk-discount rule. The task manifest declares the evidence and constraints that a reviewer considers material. Two packet fixtures show the difference between vague intent and a bounded engineering handoff.

## Run

From the course repository root:

```powershell
python examples/module-03/context-packet/packet_check.py examples/module-03/context-packet/task.json examples/module-03/context-packet/packets/structured-context.md
python examples/module-03/context-packet/packet_check.py examples/module-03/context-packet/task.json examples/module-03/context-packet/packets/weak-context.md
python -m unittest discover -s examples/module-03/context-packet/tests -v
```

The structured fixture exits 0. The weak fixture exits 1 by design. The report includes a bounded score, context precision, selected paths, and issue names; it never echoes detected secret-like values.

## What the score means

The ten points cover goal, required context, selection precision, path/rationale quality, constraints, deliverable, exact validation, stop behavior, and privacy boundary. The score proves only those declared properties. It does not predict universal model quality or replace execution, tests, diff review, or human acceptance.

## Safe learner workflow and RAG handoff

Copy `packets/learner-context.md`, edit the copy, and evaluate it against `task.json`. Do not edit the task manifest or checker to make a packet pass. Then run the shared RAG reference using the commands in [the RAG README](../../rag-reference/README.md). Preserve the same Goal, Constraints, Validation, and Stop contract while replacing pasted/static facts with policy-filtered citations. Use only synthetic course fixtures.
