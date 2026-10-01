# Module 7 Change Workflow

This dependency-free example separates two questions:

1. Did the repository change behave correctly? Run the solution repository's four tests.
2. Is the implementation handoff complete and bounded? Run `workflow_check.py` against an evidence record.

No command calls a model, accesses the network, changes Git state, or reads credentials.

Use the fixture after an approved Plan is converted into a bounded task/model and Goal contract: actual model/reasoning, unchanged Astra authority, allowed paths, four acceptance cases, one writer, review gate, time/token budget, attributed escalation trigger, and stop conditions. A `/side` conversation or read-only subagent may inspect evidence; it must not become an unowned writer. The slash commands are taught interactively and are not required to run this offline example.

## Demonstration

Run this block from `examples/module-07/change-workflow`.

```powershell
python workflow_check.py task.json evidence/complete.json
python workflow_check.py task.json evidence/unsafe.json
python -m unittest discover -s tests -v
Push-Location solution-repo
python -m unittest discover -s tests -v
Pop-Location
```

The first record is accepted. The unsafe record is rejected. The checker has ten tests; the solution repository has four. Copy `starter-repo` to a disposable directory for the lab rather than editing the canonical fixture.
