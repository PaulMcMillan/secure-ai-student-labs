# M06 — Earlier cost-decision fixture

**For the current slides, use [Model choice and reasoning effort](../README.md).** That twenty-minute paired activity replaces this fixture as the main M06 exercise. It compares GPT-5.5 and GPT-6 Astra, each at its lowest and highest available reasoning effort.

The scripts below remain available for earlier workbook users and optional accounting practice. Their factor scores and escalation thresholds are illustrative rules, not recommendations for choosing settings in the revised lesson.

The dependency-free `decision.py` recommends a generic workload role (`fast`, `balanced`, or `quality`) and escalation gate from synthetic factors. `cost_trace.py` then validates an immutable prompt/evaluation/authority comparison contract and calculates observed API, tool, reviewer, retry, and cost-per-accepted-task evidence across GPT-5.6 Luna, Terra, Sol, and GPT-6 Astra. The trace maps current model roles and prices only as a **2026-09-18 snapshot**; refresh it before delivery and never treat its small sample as a routing policy.

```powershell
python examples/module-06/cost-decision/decision.py examples/module-06/cost-decision/scenarios/routine.json
python examples/module-06/cost-decision/decision.py examples/module-06/cost-decision/scenarios/high-risk.json
python examples/module-06/cost-decision/cost_trace.py examples/module-06/cost-decision/traces/model-eval-2026-09-18.json
python -m unittest discover -s examples/module-06/cost-decision/tests -v
```
