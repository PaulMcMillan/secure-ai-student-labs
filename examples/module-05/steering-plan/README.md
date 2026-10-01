# Module 5 steering-plan example

This dependency-free checker compares a steering plan with a synthetic bounded task. It also requires a GPT-5.6/Astra task/model contract with an immutable authority and evaluation profile. Course postures and this schema are teaching vocabulary, not claims about built-in Codex modes or configuration keys.

```powershell
python examples/module-05/steering-plan/steering_check.py examples/module-05/steering-plan/task.json examples/module-05/steering-plan/plans/structured.json
python examples/module-05/steering-plan/steering_check.py examples/module-05/steering-plan/task.json examples/module-05/steering-plan/plans/unsafe.json
python -m unittest discover -s examples/module-05/steering-plan/tests -v
```

The structured plan exits 0. The unsafe plan exits 1 because it omits the model contract, skips planning/testing, and expands scope. Eight tests cover sequence, scope, constraints, evidence, stopping, and model/authority invariance.
