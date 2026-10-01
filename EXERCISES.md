# Student exercises

Start with the directions for your current module below. They include starting files, actions, checks, and what to keep. Use your own notes; you do not need the Word workbook to follow the revised practical directions. M03 explicitly lists unsupported steps to skip. Use the revised M04 and M06 activities with the current slides.

## M04 — Current slide exercise

**[Writing useful project instructions](examples/module-04/README.md)** uses a small order calculator with four passing baseline tests. Students supply a delivery policy that the code cannot reveal, record it in project guidance, and check the implementation at the exact free-delivery threshold. An independent checker stays outside the agent's working copy.

Prepare an independent copy from this repository root:

```sh
python scripts/prepare_m04.py ../m04-work
```

Open the new `m04-work` folder in your coding agent. Follow the [complete M04 directions](WORKBOOK_GUIDE.md#m04--repository-guidance), or the summary on **M04 S014**. Keep the workbook guide outside the agent's working project. The copied starter includes no assignment, worked answers, or instructor files.

## M06 — Current slide exercise

**[Model choice and reasoning effort](examples/module-06/README.md)** is a twenty-minute live model activity in pairs (allow thirty minutes alone). Investigate a payment replay with **GPT-5.5** and **GPT-6 Astra**, each at its lowest and highest available reasoning effort. Reconcile two stream cuts, diagnose defective code, and review proposed regression tests. A Python checker verifies the balance data; students also check whether each diagnosis and test expectation is correct.

An eight-minute [follow-on review](examples/module-06/README.md#follow-on-review) asks GPT-6 Astra to identify and correct mistakes in the GPT-5.5 low answer. A saved live answer is included when needed.

First, follow the [Codex project setup](examples/module-06/README.md#set-up-your-codex-project). Create a new Codex project with **examples/module-06/starter-repo** in your existing student checkout as its only folder and working root. The exercise remains part of the student repository.

## Module exercises

Follow the numbered steps in the linked guide section. M00 is optional, M01 is hands-on setup, and the earlier M04 tracing fixture is supplemental.

| Module | Starting point | Student task or directions |
| --- | --- | --- |
| M00 | [Foundations](examples/module-00/README.md) | [Choose one optional activity](WORKBOOK_GUIDE.md#m00--foundations-and-context-budgeting) |
| M01 | [Hands-on practice](examples/module-01/hands-on/README.md) | [Connect, edit, and check](WORKBOOK_GUIDE.md#m01--hands-on-setup) |
| M02 | [Order service](examples/module-02/order-service/README.md) | [Complete M02 directions](WORKBOOK_GUIDE.md#m02--bounded-coding-change) |
| M03 | [RAG exercise](examples/module-03/README.md) | [Offline RAG directions](WORKBOOK_GUIDE.md#m03--authorized-rag-trace) |
| M04 | [Guidance workshop](examples/module-04/README.md) | [Write, try, and revise instructions](WORKBOOK_GUIDE.md#m04--repository-guidance) |
| M05 | [Steering](examples/module-05/steering-plan/README.md) | [Steering activity](WORKBOOK_GUIDE.md#m05--steering-and-bounded-plans) |
| M06 | [Model choice and reasoning](examples/module-06/README.md) | [Live reconciliation activity](WORKBOOK_GUIDE.md#m06--model-choice-and-reasoning-effort) |
| M07 | [Inventory starter](examples/module-07/change-workflow/starter-repo/README.md) | [Implement, review, and hand off](WORKBOOK_GUIDE.md#m07--implement-test-review-hand-off) |
| M08 | [MCP integration](examples/module-08/stateless-mcp/README.md) | [Dossier activity](WORKBOOK_GUIDE.md#m08--mcp-integration-dossier) |
| M09 | [Tool selection](examples/module-09/tool-selection/README.md) | [Choose roles and write a handoff](WORKBOOK_GUIDE.md#m09--tool-selection) |
| M10 | [Lifecycle gates](examples/module-10/lifecycle-gates/README.md) | [Build the lifecycle contract](WORKBOOK_GUIDE.md#m10--lifecycle-gates) |
| M11 | [Merge safety](examples/module-11/task-merge-safety/README.md) | [Plan and check integration](WORKBOOK_GUIDE.md#m11--parallel-work-and-merge-safety) |
| M12 | [Release evidence](examples/module-12/release-evidence/README.md) | [Complete and defend the capstone](WORKBOOK_GUIDE.md#m12--release-evidence-capstone) |
| M12.5 | [Practice check](examples/module-12-5/practice-check/README.md) | [Build the practice packet](WORKBOOK_GUIDE.md#m125--optional-practice-check) |

Use the [exercise guide](WORKBOOK_GUIDE.md) for commands, prerequisites, and fallbacks. Some older activities include reference records or reference solutions; they are separate from the M04 starter. Open only the intended project with your agent.
