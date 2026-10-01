# Workbook exercise guide

Use this guide with the published Day 1 and Day 2 student workbooks. It maps the existing source fixtures to the current teaching order and provides corrected commands. It does not replace the workbook's discussion questions, timing, or grading guidance.

## Before starting

- Use Python 3.11+ and a disposable copy or your own branch.
- Run each code-block line separately from the repository root unless a `cd` is shown.
- For every activity, keep the task/boundary, commands, actual results, review, remaining risks, and stop decision in your workbook evidence record.
- A reference record is an example. Do not submit its claims as evidence that you performed the work.
- The ZIP contains source but no Git history. Clone if you need `git diff`, branches, or an immutable starting commit; otherwise use the workbook's disposable-copy workflow and record that limitation.

## M00 — Foundations and context budgeting

Complete the exact-token, context-manifest, and budget worksheets in the Day 1 workbook. The named tokenizer is a separate tool requirement; no tokenizer script is included. See [M00 notes](examples/module-00/README.md). The [foundations checker](examples/secure-ai-foundations/README.md) is optional evidence-packet practice.

## M01 — Setup evidence

Start with [setup-check](examples/module-01/setup-check/README.md). Inspect the safe and unsafe TOML fixtures; they are teaching data, not configuration to install.

```sh
python examples/module-01/setup-check/setup_check.py
python examples/module-01/setup-check/config_guard.py examples/module-01/setup-check/configs/safe-project.toml
python examples/module-01/setup-check/config_guard.py examples/module-01/setup-check/configs/safe-permission-profile.toml
python examples/module-01/setup-check/config_guard.py examples/module-01/setup-check/configs/unsafe-project.toml
python examples/module-01/setup-check/config_guard.py examples/module-01/setup-check/configs/unsafe-mixed-permissions.toml
python -m unittest discover -s examples/module-01/setup-check/tests -v
```

Expected: safe fixtures exit `0`, unsafe fixtures exit `1`, and **11 tests pass**. Setup evidence reflects the tools actually installed; an unavailable Codex client is a diagnostic finding. Record configuration precedence, permission boundaries, and the layer that needs attention. Use [workload identity](examples/module-01/workload-identity/README.md) for optional identity-contract practice.

## M02 — Bounded coding change

The M02 exercise is in `examples/module-02/order-service`.

1. Read the [lab README](examples/module-02/order-service/README.md), [repository guidance](examples/module-02/order-service/AGENTS.md), and [work item](examples/module-02/order-service/WORK_ITEM.md).
2. Run the baseline from this repository root:

   ```sh
   python -m unittest discover -s examples/module-02/order-service/tests -v
   ```

   Expected: **4 tests pass**. The starter intentionally does not reject zero or negative quantities; implementing that behavior is the exercise.

3. In your own copy or branch, add the requested negative-case test and the smallest quantity-validation change. Preserve valid totals and currency rounding.
4. Rerun the tests and review your changes. Record commands, results, and remaining risks in the workbook.

## M03 — Authorized RAG trace

This offline lab ingests synthetic policy documents, filters access before ranking, returns cited answers or abstains, and records redacted telemetry.

### 1. Build the index

```sh
python examples/rag-reference/rag.py ingest --manifest examples/rag-reference/corpus/manifest.json --index examples/rag-reference/build/index.json
```

Expected: **7 source documents, 5 indexed documents, 5 chunks**. One sample is quarantined and one is pending deletion.

### 2. Ask an authorized question

```sh
python examples/rag-reference/rag.py query --index examples/rag-reference/build/index.json --principal learner-alpha --tenant northstar --roles employee --clearances internal --question "What is the travel approval threshold?" --telemetry examples/rag-reference/build/telemetry.jsonl
```

Expected: `status: answered`, an answer containing **$500**, and a citation to `northstar-travel-2026`.

### 3. Check a denied-access case

```sh
python examples/rag-reference/rag.py query --index examples/rag-reference/build/index.json --principal learner-alpha --tenant northstar --roles employee --clearances internal --question "What is the Southstar acquisition project codename?" --telemetry examples/rag-reference/build/telemetry.jsonl
```

Expected: `status: abstained` and no citations to the other tenant's document.

### 4. Run the evaluation and tests

```sh
python examples/rag-reference/rag.py eval --index examples/rag-reference/build/index.json --cases examples/rag-reference/evals/cases.json --telemetry examples/rag-reference/build/telemetry.jsonl
python -m unittest discover -s examples/rag-reference/tests -v
```

Expected: **8/8 evaluation cases** and **9 unit tests pass**. The evaluation covers answerable queries, abstention, classification, cross-tenant access, poisoned content, freshness, deletion, and budget limits.

Use the results and `build/telemetry.jsonl` for your workbook evidence record. The generated index and telemetry stay out of Git.

### Scope of this reference

The implementation uses lexical retrieval and a deterministic answer composer. It supports the offline authorization and evidence exercises. The workbook's optional full vector/hybrid search, reranking, and LLM extension requires additional implementation and an approved environment. See the [RAG README](examples/rag-reference/README.md) and [runbook](examples/rag-reference/RUNBOOK.md) for details.


## M04 — Repository guidance

Start with [instruction-chain](examples/module-04/instruction-chain/README.md). The nested `AGENTS.md` files are synthetic inputs for this exercise; inspect the selected files and their order.

```sh
python examples/module-04/instruction-chain/instruction_trace.py examples/module-04/instruction-chain/scenarios/payments.json
python examples/module-04/instruction-chain/instruction_trace.py examples/module-04/instruction-chain/scenarios/catalog.json
python examples/module-04/instruction-chain/instruction_trace.py examples/module-04/instruction-chain/scenarios/untrusted-payments.json
python examples/module-04/instruction-chain/instruction_trace.py examples/module-04/instruction-chain/scenarios/multi-folder.json
python examples/module-04/instruction-chain/guidance_lint.py examples/module-04/instruction-chain/fixture/repo/AGENTS.md
python -m unittest discover -s examples/module-04/instruction-chain/tests -v
```

Expected: **9 tests pass**. Explain the winning test command, the modeled trust gate, and why a secondary folder's guidance is not automatically loaded. Record your trace and guidance review.

## M05 — Steering and bounded plans

Read [steering-plan/task.json](examples/module-05/steering-plan/task.json). Compare the structured and unsafe phases, then draft your corrected-threshold steer and bounded task contract using the [prompt templates](examples/module-05/prompt-loop/README.md).

```sh
python examples/module-05/steering-plan/steering_check.py examples/module-05/steering-plan/task.json examples/module-05/steering-plan/plans/structured.json
python examples/module-05/steering-plan/steering_check.py examples/module-05/steering-plan/task.json examples/module-05/steering-plan/plans/unsafe.json
python -m unittest discover -s examples/module-05/steering-plan/tests -v
```

Expected: structured exits `0`, unsafe exits `1`, and **8 tests pass**. The workbook's seven-test count predates the extra contract check. Submit the routing rationale, five-phase contract, checkpoints, budget, and stop conditions.

## M06 — Cost per accepted task

Read [cost-decision](examples/module-06/cost-decision/README.md). Compare routine and high-risk workload decisions and inspect the supplied synthetic cost trace.

```sh
python examples/module-06/cost-decision/decision.py examples/module-06/cost-decision/scenarios/routine.json
python examples/module-06/cost-decision/decision.py examples/module-06/cost-decision/scenarios/high-risk.json
python examples/module-06/cost-decision/cost_trace.py examples/module-06/cost-decision/traces/model-eval-2026-09-18.json
python -m unittest discover -s examples/module-06/cost-decision/tests -v
```

Expected: **12 tests pass**. Verify one candidate's cost-per-accepted-task calculation by hand, including failed runs, tools, and reviewer labor. Record baseline choice, escalation gates, assumptions, and the trace date. The supplied prices/model labels are a course snapshot.

## M07 — Implement, test, review, hand off

Use a disposable copy of [starter-repo](examples/module-07/change-workflow/starter-repo/README.md). Read its `AGENTS.md` and `WORK_ITEM.md`; add the missing zero/negative-quantity cases and the smallest guard in `src/inventory.py`.

```sh
cd examples/module-07/change-workflow/starter-repo
python -m unittest discover -s tests -v
cd ../../../..
```

Expected baseline: **2 tests**. After the workbook change: **4 acceptance tests**. Compare [solution-repo](examples/module-07/change-workflow/solution-repo/README.md) after your attempt. Run its tests from inside that directory too.

Validate the supplied handoff records:

```sh
python examples/module-07/change-workflow/workflow_check.py examples/module-07/change-workflow/task.json examples/module-07/change-workflow/evidence/complete.json
python examples/module-07/change-workflow/workflow_check.py examples/module-07/change-workflow/task.json examples/module-07/change-workflow/evidence/unsafe.json
python -m unittest discover -s examples/module-07/change-workflow/tests -v
```

Expected: complete exits `0`, unsafe exits `1`, and **10 checker tests pass**. Submit your contract, changed files, tests, diff review, adjudication, and stopping decision.

## M08 — MCP integration dossier

Use the [stateless fixture](examples/module-08/stateless-mcp/README.md), inspect `server.py`, `client.py`, and `risk-dossier.json`, then create your boundary map and control/removal plan.

```sh
python examples/module-08/stateless-mcp/client.py
python examples/module-08/stateless-mcp/dossier_check.py examples/module-08/stateless-mcp/risk-dossier.json
python -m unittest discover -s examples/module-08/stateless-mcp/tests -v
```

Expected: three independent responses, one `lookup_policy` tool, a valid dossier, and **12 tests pass**. Optional: [MCP security](examples/module-08/mcp-security/README.md) and [RAG bridge](examples/module-08/rag-mcp-bridge/README.md). The `local-mcp` fixture is a legacy migration comparison, not this workbook's core lab.

## M09 — Tool selection

Inspect [tool-selection/scenarios](examples/module-09/tool-selection/scenarios). Choose a single-tool or bounded sequential workflow based on task evidence, with one writer and a distinct reviewer.

```sh
python examples/module-09/tool-selection/decision.py examples/module-09/tool-selection/scenarios/bounded-sequence.json
python examples/module-09/tool-selection/decision.py examples/module-09/tool-selection/scenarios/unsafe-dual-edit.json
python -m unittest discover -s examples/module-09/tool-selection/tests -v
```

Expected: bounded sequence exits `0`, unsafe dual edit exits `1`, and **10 tests pass**. Submit your selection rationale and handoff contract. These scripts evaluate records; they do not start Codex or Claude Code.

## Shared RAG evidence for M10–M12.5

Keep `examples/rag-reference`, `examples/evidence/EV-RAG-01.json`, and `examples/rag_evidence_binding.py` together. The later checkers verify the observation and source hashes. Run the M03 ingest/query/eval commands to obtain your own functional output; `python scripts/validate_course.py` also reruns that behavior in a temporary directory.

M10, M11, and M12.5 consume the pre-staged observation. M12 additionally asks you to execute the RAG path and retain real output. Do not edit the shared corpus or evidence to make a checker pass. An evidence record passing its checker proves its structure and bindings, not a real approval or deployment.

## M10 — Lifecycle gates

Copy [evidence/starter.json](examples/module-10/lifecycle-gates/evidence/starter.json) for your work. Inspect `task.json`, complete the state transitions and gates, and compare with the supplied complete and unsafe records.

```sh
python examples/module-10/lifecycle-gates/workflow_check.py examples/module-10/lifecycle-gates/task.json examples/module-10/lifecycle-gates/evidence/complete.json
python examples/module-10/lifecycle-gates/workflow_check.py examples/module-10/lifecycle-gates/task.json examples/module-10/lifecycle-gates/evidence/unsafe.json
python -m unittest discover -s examples/module-10/lifecycle-gates/tests -v
```

Expected: complete exits `0`, unsafe exits `1`, and **12 tests pass**. Record the lifecycle, authority at each state, evidence gates, recovery, monitoring, and release decision.

## M11 — Parallel work and merge safety

Start with [evidence/starter.json](examples/module-11/task-merge-safety/evidence/starter.json) and `task.json`. Design the graph and waves, disjoint output ownership, shared immutable RAG release, independent review, and one integration decision.

```sh
python examples/module-11/task-merge-safety/merge_check.py examples/module-11/task-merge-safety/task.json examples/module-11/task-merge-safety/evidence/complete.json
python examples/module-11/task-merge-safety/merge_check.py examples/module-11/task-merge-safety/task.json examples/module-11/task-merge-safety/evidence/unsafe.json
python -m unittest discover -s examples/module-11/task-merge-safety/tests -v
```

Expected: complete exits `0`, unsafe exits `1`, and **12 tests pass**. Submit graph/waves, role contracts, write ownership, review/integration gates, and stop conditions. Running this checker does not spawn agents or merge code.

## M12 — Release-evidence capstone

Work in a disposable copy of [starter](examples/module-12/release-evidence/starter), following [task.json](examples/module-12/release-evidence/task.json). Add `explain_quote` and the required tests while preserving `quote_total`. Start your evidence record from [evidence/starter.json](examples/module-12/release-evidence/evidence/starter.json).

```sh
python -m unittest discover -s examples/module-12/release-evidence/starter/tests -v
python -m unittest discover -s examples/module-12/release-evidence/solution/tests -v
python examples/module-12/release-evidence/evidence_check.py examples/module-12/release-evidence/task.json examples/module-12/release-evidence/evidence/complete.json
python examples/module-12/release-evidence/evidence_check.py examples/module-12/release-evidence/task.json examples/module-12/release-evidence/evidence/unsafe.json
python -m unittest discover -s examples/module-12/release-evidence/tests -v
```

Expected: **2 starter tests**, **5 reference-solution tests**, complete exit `0`, unsafe exit `1`, and **13 checker tests**. Open the solution after attempting the change. Also run the M03 RAG commands and keep their actual output. Submit your bounded change, eleven-domain evidence index, independent review/adjudication, release/recovery decision, and paired defense.

## M12.5 — Optional practice check

Use [records/starter.json](examples/module-12-5/practice-check/records/starter.json) and `task.json` to build the twelve-practice packet. Compare complete and unsafe records after your attempt.

```sh
python examples/module-12-5/practice-check/practice_check.py examples/module-12-5/practice-check/task.json examples/module-12-5/practice-check/records/complete.json
python examples/module-12-5/practice-check/practice_check.py examples/module-12-5/practice-check/task.json examples/module-12-5/practice-check/records/unsafe.json
python -m unittest discover -s examples/module-12-5/practice-check/tests -v
```

Expected: complete exits `0` with 12 practices and the separate RAG operations gate; unsafe exits `1`; **14 tests pass**. Submit the packet, checker reports, adoption/retrospective notes, and stop record.

## Supplemental scenario numbering

The [security task range](examples/security-task-range/README.md) retains its original storyline IDs: its M01 boundary-mapping episode fits current workbook M02, and its M02 setup episode fits current workbook M01. Treat these as scenario identifiers, not repository directory names. The remaining numbered scenarios support their corresponding modules.

See the [repository README](README.md#supplemental-exercises) for all other optional fixtures. Exact CLI working directories are stated in each fixture README.
