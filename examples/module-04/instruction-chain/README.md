# Module 4 layered-instruction example

This dependency-free example traces documented `AGENTS.md` selection and merge behavior, the project-trust gate, and primary-folder discovery in a synthetic tree. It does not launch Codex, read the real user home, or change configuration or trust state.

```powershell
python examples/module-04/instruction-chain/instruction_trace.py examples/module-04/instruction-chain/scenarios/payments.json
python examples/module-04/instruction-chain/instruction_trace.py examples/module-04/instruction-chain/scenarios/untrusted-payments.json
python examples/module-04/instruction-chain/instruction_trace.py examples/module-04/instruction-chain/scenarios/multi-folder.json
python examples/module-04/instruction-chain/guidance_lint.py examples/module-04/instruction-chain/fixture/repo/AGENTS.md
python -m unittest discover -s examples/module-04/instruction-chain/tests -v
```

For trusted projects, the tracer chooses one non-empty file per directory using override, standard, then configured fallback order. It merges broad to specific and reports effective course-fixture rules. For an untrusted project it retains global guidance but skips project guidance. In a multi-folder scenario it reports the primary automatic guidance root and treats secondary folders as visible content, not additional automatic guidance roots. The linter checks the teaching structure only; it is not an OpenAI product requirement.

These behaviors are update-sensitive and were verified against official Codex documentation/changelog on 2026-09-10.
