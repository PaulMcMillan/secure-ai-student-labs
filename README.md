# Secure AI Agentic Platform Engineering — Student Labs

Exercise source, tests, and synthetic data for the Day 1 and Day 2 student workbooks.

**[Exercise index](EXERCISES.md)** · **[Download ZIP](https://github.com/PaulMcMillan/secure-ai-student-labs/archive/refs/heads/main.zip)** · **[Workbook exercise guide](WORKBOOK_GUIDE.md)**

## Get started

```sh
git clone https://github.com/PaulMcMillan/secure-ai-student-labs.git
cd secure-ai-student-labs
python --version
python scripts/validate_course.py
```

If you already cloned this repository, run `git pull` after saving your exercise changes. ZIP users can download and extract a fresh copy.

Use **Python 3.11 or newer**. The bundled fixtures need only the standard library. Substitute `python3` or `py -3` if that is your Python command. Run commands from the repository root unless a lab explicitly names another working directory.

The validation command runs **235 tests across 27 suites**, then rebuilds the RAG index in a temporary directory, runs a cited query, and checks **8 evaluation cases** against the supplied observation. Setup diagnostics may invoke installed Git/Codex status commands; no model API is required. The optional tokenizer homework and live coding-assistant activities have separate tool requirements described in the workbook.

## Find your workbook module

| Day | Module | Exercise | Included support |
| --- | --- | --- | --- |
| 1 | M00 | [Foundations and context budgeting](examples/module-00/README.md) | Written homework; supplemental evidence checker |
| 1 | M01 | [Setup and sanitized evidence](examples/module-01/setup-check/README.md) | Setup checker and configuration fixtures |
| 1 | M02 | [Bounded coding change](examples/module-02/order-service/README.md) | Order-service starter and baseline tests |
| 1 | M03 | [Authorized RAG trace](examples/module-03/README.md) | Offline RAG; skip missing hybrid/LLM steps as directed in the guide |
| 1 | M04 | [Writing project guidance](examples/module-04/README.md) | Standalone order-calculator starter for the revised slides |
| 1 | M05 | [Steering and bounded plans](examples/module-05/steering-plan/README.md) | Plan checker and prompt templates |
| 1 | M06 | [Cost per accepted task](examples/module-06/cost-decision/README.md) | Role decisions and synthetic cost trace |
| 2 | M07 | [Implement, test, review, hand off](examples/module-07/change-workflow/README.md) | Inventory starter, reference solution, evidence checker |
| 2 | M08 | [MCP integration dossier](examples/module-08/stateless-mcp/README.md) | STDIO client/server and dossier checker |
| 2 | M09 | [Tool selection](examples/module-09/tool-selection/README.md) | Workflow scenarios and decision checker |
| 2 | M10 | [Lifecycle gates](examples/module-10/lifecycle-gates/README.md) | Starter, complete, and unsafe RAG release records |
| 2 | M11 | [Parallel work and merge safety](examples/module-11/task-merge-safety/README.md) | Task graphs, evidence records, and merge checker |
| 2 | M12 | [Release-evidence capstone](examples/module-12/release-evidence/README.md) | Pricing starter/solution and RAG release evidence |
| 2 | M12.5 | [Optional practice check](examples/module-12-5/practice-check/README.md) | Twelve-practice evidence packet and checker |

Start with the [exercise index](EXERCISES.md). For M04, run `python scripts/prepare_m04.py ../m04-work` from this repository root, then open the new `m04-work` folder in your coding agent. The [M04 workbook directions](WORKBOOK_GUIDE.md#m04--repository-guidance) and the work slide describe the same activity. Keep the workbook guide outside the agent's working project. The [workbook guide](WORKBOOK_GUIDE.md) retains commands and records for the other existing exercises.

## Supplemental exercises

These existing fixtures support additional practice. Follow the core workbook activity first.

| Fits with | Exercise | Purpose |
| --- | --- | --- |
| M00 | [Secure AI foundations](examples/secure-ai-foundations/README.md) | Compare declared controls with synthetic evidence |
| M01 | [Workload identity](examples/module-01/workload-identity/README.md) | Evaluate identity, isolation, and authorization contracts |
| M02 | [Lint repair](examples/module-02/lint-repair/README.md) | Repair one lint issue while preserving behavior |
| M03 | [Context packet](examples/module-03/context-packet/README.md) | Build a bounded handoff using relevant repository context |
| M04, earlier workbook | [Instruction-chain tracing](examples/module-04/instruction-chain/README.md) | Earlier workbook fixture, separate from the revised slide activity |
| M05 | [Prompt and bounded-loop templates](examples/module-05/prompt-loop/README.md) | Write a plan, steer, and stopping contract |
| M08 | [MCP security](examples/module-08/mcp-security/README.md) | Evaluate policy records and incident events |
| M03 / M08 | [RAG MCP bridge](examples/module-08/rag-mcp-bridge/README.md) | Expose the shared offline RAG through a read-only tool |
| M08 | [Legacy MCP comparison](examples/module-08/local-mcp/README.md) | Compare the older handshake with the course's stateless fixture |
| Across modules | [Security task range](examples/security-task-range/README.md) | Evaluate inert scenario records against control sets |

## Path corrections and scope

- **M01:** setup now lives in `examples/module-01/setup-check`; workload identity is in `examples/module-01/workload-identity`.
- **M02:** the coding lab is `examples/module-02/order-service`; optional lint repair is `examples/module-02/lint-repair`.
- **M03:** start at `examples/module-03/README.md`. The shared RAG code stays in `examples/rag-reference` because M08 and M10–M12.5 also use its paths and integrity-bound evidence.
- Older workbooks may print the historical M01/M02 folder names or `course/.../lab-guide.md` authoring paths. Use the corrected paths and separate command lines in [WORKBOOK_GUIDE.md](WORKBOOK_GUIDE.md).
- The workbook's exact-token/context-budget homework is a written/tool-based activity. The repository contains no tokenizer script. For M03, complete the offline exercise and **skip** the missing full-workbook features listed in the guide, including hybrid search, reranking, LLM calls, and automatic retry/clarification. Record them as skipped; no extra model setup is required.

Work in your own copy or branch. Starter tests deliberately cover baseline behavior; add the acceptance tests the workbook asks for. Compare reference solutions after attempting the change. Unsafe/incomplete records usually exit `1` by design; successful rejection is part of the exercise.

All policy records, identities, and corpus data are synthetic classroom fixtures. The security range evaluates inert data and does not execute attacks. Evidence checkers validate file bindings and recorded structure; they do not establish that a real agent, approval, review, or deployment occurred. Model, pricing, configuration, and protocol references are dated course examples; consult your instructor's current guidance for live tools.

Use the separately supplied student workbooks and slides alongside this repository. Instructor guides, exam materials, and student records are not included.
