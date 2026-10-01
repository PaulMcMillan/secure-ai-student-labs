# Module 6 cost-decision example

The dependency-free `decision.py` recommends a generic workload role (`fast`, `balanced`, or `quality`) and escalation gate from synthetic factors. `cost_trace.py` then validates an immutable prompt/evaluation/authority comparison contract and calculates observed API, tool, reviewer, retry, and cost-per-accepted-task evidence across GPT-5.6 Luna, Terra, Sol, and GPT-6 Astra. The trace maps current model roles and prices only as a **2026-09-18 snapshot**; refresh it before delivery and never treat its small sample as a routing policy.

```powershell
python examples/module-06/cost-decision/decision.py examples/module-06/cost-decision/scenarios/routine.json
python examples/module-06/cost-decision/decision.py examples/module-06/cost-decision/scenarios/high-risk.json
python examples/module-06/cost-decision/cost_trace.py examples/module-06/cost-decision/traces/model-eval-2026-09-18.json
python -m unittest discover -s examples/module-06/cost-decision/tests -v
```
