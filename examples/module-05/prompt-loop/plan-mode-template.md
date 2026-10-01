# Plan-Mode Prompt Template

```text
/plan Investigate [problem/outcome] in [repository/path/system].

Known context: [facts and source paths].
Constraints/non-goals: [scope, compatibility, data, security, authority].
Before proposing a plan, ask at most [N] questions that materially affect the
approach. Return current-state evidence, assumptions, [N] options with
tradeoffs, risks, affected checks, and a milestone plan.

Do not [edit/run writes/use network/change permissions]. Stop when [named owner]
can approve one option or when [blocking evidence] requires escalation.

Model plan: start with [GPT-5.6 lane and reasoning rationale]. Compare GPT-6
Astra only after [attributed evidence trigger], holding prompt, input, tools,
data, permissions, and evaluation constant.
```

After approval, start a separate Goal-mode contract:

```text
/goal Deliver [approved outcome]. Use [model/reasoning and rationale]. Keep
[scope, authority, and constraints]. Verify with
[tests/review/measurements]. At each checkpoint report hypothesis, evidence,
remaining attempt/tool/time/token budget, and next decision. Stop on acceptance,
exhausted budget, policy denial, unexpected scope, or a new-authority decision.
```
