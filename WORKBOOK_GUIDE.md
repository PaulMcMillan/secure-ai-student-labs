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

**Time: 20 minutes.** Use `examples/module-02/order-service` for the workbook's M02 lab. Replace any older `examples/module-01/order-service` path with this one.

You need Python 3.11+, your own writable copy, and an approved coding agent if you are doing the agent-assisted activity. Git is useful for the branch and diff evidence. No packages, model API keys, MCP server, or plugins are needed by the sample. Run every command below from the **student repository root**.

### 0–6 minutes: inspect and frame the task

Read these four files:

- [AGENTS.md](examples/module-02/order-service/AGENTS.md): applicable project instructions.
- [WORK_ITEM.md](examples/module-02/order-service/WORK_ITEM.md): goal, constraints, and acceptance criteria.
- [pricing.py](examples/module-02/order-service/src/order_service/pricing.py): starter implementation.
- [test_pricing.py](examples/module-02/order-service/tests/test_pricing.py): baseline tests.

In a cloned repository, record the starting status and create your own branch:

```sh
git status --short --branch
git switch -c student/m02-quantity-validation
python -m unittest discover -s examples/module-02/order-service/tests -v
```

Choose another branch name if that one exists. If you downloaded a ZIP, use a disposable extracted copy, skip the Git commands, and record “ZIP copy; branch/diff commands not run.” Use your editor to compare your changes with a second untouched copy.

**Checkpoint:** four baseline tests pass. They cover valid totals, empty orders, multiple lines, and rounding. They do not yet prove that invalid quantities are rejected. If the baseline fails, stop and check your Python command, working directory, and whether the starter has already been edited.

Write one line for each field below, then give that contract to your coding agent. Keep the allowed paths relative to `examples/module-02/order-service`:

| Field | What your contract must say |
| --- | --- |
| Goal | Reject every line whose quantity is below 1, raising `ValueError` with exactly `quantity must be at least 1`. |
| Context | Read the four files above. The current four tests pass; quantity validation is missing. |
| Constraints | Change only `src/order_service/pricing.py` and `tests/test_pricing.py`. Preserve the public function signature, valid totals, `Decimal`, and `ROUND_HALF_UP`. Add no dependencies or unrelated refactoring. Use no network, credentials, plugins, or MCP server. |
| Validation | Show a new invalid-quantity test failing on the starter, then passing after the change. Run the entire sample suite and review the diff. |
| Stop | Stop after the acceptance checks and review, or report a failing baseline, conflicting instruction, or need for work outside the two allowed files. |

Record the agent surface you chose, its workspace/permission boundary, and why the task needs only file edits and local tests. Identify who sets the goal, who proposes the change, which tool reads files/runs tests, and who accepts the final diff.

### 6–14 minutes: implement the smallest change

1. Ask the agent to add **one new test method** covering zero or a negative quantity, including the exact exception message. To cover both cases while keeping five test methods, use two `subTest` cases inside that one method.
2. Run the test command above **before changing the implementation**. Record the expected failure: the starter does not raise the required exception.
3. Ask for quantity validation before subtotal/tax calculation. Preserve valid-order behavior and the function's iterable input contract; do not accidentally consume a one-shot iterator twice.
4. Rerun the same test command. Read the actual output yourself.

**Checkpoint:** five test methods pass, including the new invalid-quantity test. If you chose separate methods for zero and negative quantities, six passing methods are also valid; what matters is the acceptance behavior. Only the two permitted files should change.

### 14–18 minutes: validate and review

```sh
python -m unittest discover -s examples/module-02/order-service/tests -v
git diff -- examples/module-02/order-service
git status --short
```

Check the exact error type/message, validation order, function signature, valid totals, rounding, and two-file scope. Keep the failing-test output, passing-test output, and reviewed diff. ZIP users compare against the untouched copy instead of running Git commands.

### 18–20 minutes: explain and hand off

In two or three sentences, explain the behavioral instruction, chosen agent surface/tools, acting identity category without account identifiers, workspace boundary, any approval decision, human review, and stopping condition.

Keep your five-field contract, baseline evidence, changed files/diff, new test's failure and success, final suite result, control explanation, and any remaining uncertainty. A passing baseline alone does not complete the exercise. Keep the work for debrief; do not commit or push unless your instructor asks.

If agent access is unavailable, complete the written contract and review the starter. Pair with a learner who can run it or follow the instructor's fallback. Mark implementation and tests you did not execute “not run.”

## M03 — Authorized RAG trace

**Do the offline exercise below. Skip the missing parts of the workbook's full vertical-slice lab.** Use the supplied synthetic corpus and Python fixture; no local model setup, extra packages, or API key is required. Allow about 30 minutes for the authorized-RAG evidence activity.

### What to do and what to skip

| Workbook request | Directions for this class |
| --- | --- |
| Ingest two student documents and one instructor-only document | **Skip creating that corpus.** Inspect and ingest the seven supplied synthetic policy documents. Use their tenant, role, classification, owner, version, and date metadata. They are not actual student/instructor materials. |
| Vector plus full-text search, fusion, and reranking | **Skip vector search, fusion, and reranking.** Run the supplied lexical retrieval and inspect its scores. |
| Bounded context pack and LLM generation | **Skip building a model prompt and calling an LLM.** Inspect the selected chunks and the deterministic extractive answer with its citations. |
| Direct/no-retrieval routing, automatic retry, and clarification | **Skip implementing or demonstrating these paths.** The fixture supports an answer, abstention, or a blocked request. |
| Injection, weak evidence, stale content, and access boundaries | **Do** the supplied queries and eight-case evaluation below. Review the reason and source IDs for each result. |
| Trace, quality/operations metrics, deletion/reindex evidence | **Do** the telemetry review, existing deletion-pending evaluation case, and clean rebuild below. **Skip** live deletion workflows, hosted-model token/cost measurements, scale tests, and production latency claims. |

In your evidence record, write “skipped — not included in the supplied lab” for the omitted parts. These omissions do not block completion of this adapted offline exercise. Do not claim the full hybrid/LLM system was built or tested.

### 0–5 minutes: inspect the inputs and boundary

Run commands from the **student repository root**. Read:

- [rag.py](examples/rag-reference/rag.py): `_eligible_documents`, `answer_query`, and `_telemetry_event`.
- [corpus/manifest.json](examples/rag-reference/corpus/manifest.json): approved files and policy metadata.
- [evals/cases.json](examples/rag-reference/evals/cases.json): eight synthetic questions and expected outcomes.

The CLI identity arguments simulate verified claims from a trusted harness. `employee` is a synthetic role, not a real signed-in student identity. `internal` and `restricted` are explicit classification clearances. The reference freezes policy time at **2026-09-10** for reproducible results.

Record: your question, synthetic caller/tenant/role/clearance, permitted corpus, reason retrieval is needed, and expected citation or abstention. Explain why document text is evidence rather than an instruction to the agent. Keep the shared corpus and code unchanged so later modules can use their evidence hashes.

### 5–10 minutes: ingest and ask an authorized question

The commands save JSON results under the existing, Git-ignored `build` folder. Open each output file in your editor after running it. A query that abstains can still exit `0`; inspect `status` and `reason`, not only the process exit code.

```sh
python examples/rag-reference/rag.py ingest --manifest examples/rag-reference/corpus/manifest.json --index examples/rag-reference/build/index.json > examples/rag-reference/build/ingest-output.json
python examples/rag-reference/rag.py query --index examples/rag-reference/build/index.json --principal learner-alpha --tenant northstar --roles employee --clearances internal --question "What is the travel approval threshold?" --telemetry examples/rag-reference/build/telemetry.jsonl > examples/rag-reference/build/authorized-answer.json
```

Expected ingestion: **7 source documents, 5 indexed documents, 5 chunks**, one quarantined document, and one deletion-pending document. “Indexed” does not mean every caller may retrieve a document; policy filtering happens before scoring.

Expected answer: `status: answered`, text containing **$500**, and a citation to `northstar-travel-2026`. Record `trace_id`, `index_version`, `integrity_sha256`, `policy_decision`, and the retrieved/cited source IDs. Open `corpus/documents/travel-policy.md` and check that it supports the claim and citation. In `answer_query`, locate the filtering step before the ranking step.

### 10–18 minutes: check denied access and the evaluation cases

Run three access checks using the same index:

```sh
python examples/rag-reference/rag.py query --index examples/rag-reference/build/index.json --principal learner-alpha --tenant northstar --roles employee --clearances internal --question "What is the Southstar acquisition project codename?" --telemetry examples/rag-reference/build/telemetry.jsonl > examples/rag-reference/build/denied-tenant.json
python examples/rag-reference/rag.py query --index examples/rag-reference/build/index.json --principal learner-alpha --tenant northstar --roles employee --clearances internal --question "What must happen before a consequential production action?" --telemetry examples/rag-reference/build/telemetry.jsonl > examples/rag-reference/build/denied-classification.json
python examples/rag-reference/rag.py query --index examples/rag-reference/build/index.json --principal learner-visitor --tenant northstar --roles visitor --clearances internal --question "What is the travel approval threshold?" --telemetry examples/rag-reference/build/telemetry.jsonl > examples/rag-reference/build/denied-role.json
python examples/rag-reference/rag.py eval --index examples/rag-reference/build/index.json --cases examples/rag-reference/evals/cases.json --telemetry examples/rag-reference/build/telemetry.jsonl --report examples/rag-reference/build/eval-report.json
python -m unittest discover -s examples/rag-reference/tests -v
```

Expected: all three access queries have `status: abstained`, empty answers, and empty citations. The other tenant's source, the restricted source, and the role-denied travel source must be absent from the respective `retrieved` lists. **8/8 evaluation cases and 9 unit tests pass**; the ten reported evaluation metrics equal `1.0` for this small fixture.

In `eval-report.json`, inspect every row:

| Case | Evidence to explain |
| --- | --- |
| RAG-E01 — answerable | The permitted travel policy supports the cited answer. |
| RAG-E02 — abstain | The corpus does not support the lunar-commuting question. |
| RAG-E03 — classification | Internal clearance does not admit the restricted security standard. |
| RAG-E04 — cross-tenant | Northstar cannot retrieve Southstar's private source. |
| RAG-E05 — poison | The bundled malicious-instruction sample is quarantined and not retrieved. This demonstrates a known-sample check, not general prompt-injection immunity. |
| RAG-E06 — freshness | The retired meal policy is expired at the test's policy time. |
| RAG-E07 — deletion | The deletion-pending draft is excluded even at its future effective date. |
| RAG-E08 — budget | The over-budget question is blocked. |

### 18–25 minutes: inspect the trace and rebuild

Find the authorized query's `trace_id` in `build/telemetry.jsonl`. Record its source IDs, citation count, policy-filter counts, budget, and local `elapsed_ms`. Confirm `content_logged` is false and the event omits the question, answer, and raw document content. Telemetry appends on each run; use trace IDs to identify your current results.

Build a fresh index from the same trusted files and evaluate it:

```sh
python examples/rag-reference/rag.py ingest --manifest examples/rag-reference/corpus/manifest.json --index examples/rag-reference/build/rebuilt-index.json > examples/rag-reference/build/rebuild-output.json
python examples/rag-reference/rag.py eval --index examples/rag-reference/build/rebuilt-index.json --cases examples/rag-reference/evals/cases.json --report examples/rag-reference/build/rebuilt-eval-report.json
```

Compare `ingest-output.json` with `rebuild-output.json`: the integrity digest and index version should match. The rebuilt evaluation must again pass all eight cases. Combined with RAG-E07, this demonstrates rebuilding the trusted fixture while excluding a pre-marked deletion-pending source. It does not perform a live deletion operation. Skip designing a new deletion workflow for this exercise.

### 25–30 minutes: finish the evidence record

Keep the saved query/ingest/evaluation/rebuild outputs, unit-test result, and the matching telemetry events. Add a short record containing:

- Question, synthetic caller claims, permitted corpus, and retrieval decision.
- Where authorization runs before ranking and how untrusted text is handled.
- Supporting source/citation and your manual claim check.
- Tenant, role, classification, injection, freshness, and deletion-case results.
- Observed evaluation metrics, local timing, and rebuild digest comparison.
- The skipped features from the table above and your final completion or stop decision.

Do not report model tokens/cost, production latency, semantic retrieval quality, or retry/clarification behavior as measured. Stop and investigate if an unauthorized source is retrieved or any evaluation fails. Preserve your evidence for debrief; generated files stay under the ignored `build` directory.

If a command cannot find a file, return to the repository root and check the path. If the index is missing, rerun ingestion. If integrity verification fails, restore an untouched copy of the supplied fixture and rebuild; do not disable the check. Without Python, inspect the source/case files and complete the written record, marking all execution results “not run.”


## M04 — Repository guidance

This activity takes about 15 minutes once the project is ready: 2 minutes to read the brief, then 13 minutes to write, try, and revise guidance. Complete preparation before starting the timer. You will write shared and local project instructions, check a small agent-assisted change, and clarify how a rule handles an approved exception. The [order calculator starter](examples/module-04/agents-md-workshop/README.md) is self-contained and needs only Python's standard library.

Read these directions yourself. Give the agent only your project guides and the task prompts below. Keep this workbook guide outside the agent's working project.

### Before the timer: prepare the project

From the **secure-ai-student-labs root**, run:

```sh
python scripts/prepare_m04.py ../m04-work
```

Open the new **m04-work** folder as your project in the coding agent. The preparation script copies only seven starter files and, when Git is available, creates a local baseline commit for reviewing changes. It refuses to overwrite an existing destination. To try again, choose a new folder name.

From **m04-work**, run:

```sh
python -m unittest discover -s tests -v
python demo.py
```

Expected baseline: **4 passing tests** and `Order total: 13.50`. Use `python3` or `py -3` if that is your Python command. No packages, API keys, or AITrainer files are required by the sample. Use your existing coding agent for the live activity.

The repository root for the rest of this exercise is **m04-work**, not the lab collection.

```text
m04-work/
├── AGENTS.md                   starter project instructions
├── demo.py                     an example caller
├── src/order_total/pricing.py  the calculator
└── tests/test_pricing.py       automated checks
```

### 0–2 minutes: read the maintainer's brief

The maintainer looks after this project. These are the requirements they want future work to respect:

- Use Python's standard library; the project needs no extra packages.
- Keep money calculations in `Decimal`, Python's decimal number type. Converting to floating-point values can change rounding results.
- Round the final total to two decimal places with `ROUND_HALF_UP`, as the starter does.
- Ordinary fixes preserve the public function's name and parameters because other code uses them to call it.
- A maintainer can approve an interface change. That change must account for the callers and tests that use the interface.
- Finish by reviewing the changed lines and reporting the test results.

### 2–6 minutes: write two guides

Write the drafts yourself, using the brief above.

1. Open the root `AGENTS.md`. Add the small folder map, the test command and its working directory, use of the standard library, and the expectations for review and test reporting. Keep the starter public-function rule for now.
2. Create `src/order_total/AGENTS.md`. Put the money-calculation and rounding requirements there. This local guide applies to the calculator; it does not need to repeat the root guide's workflow.

A few clear sentences in each file are enough. Include the reason for a requirement when it will help someone make a decision. Headings such as `## Validation` are optional ways to organize the text.

### 6–11 minutes: make and review a small change

Start a fresh agent conversation in **m04-work**. Give it this request:

> Read `AGENTS.md` and `src/order_total/AGENTS.md`. Name both files and briefly summarize the rules that apply. Then reject order items whose quantity is zero or negative. Raise `ValueError` with the message `quantity must be at least 1`. Add tests for both cases and check the result.

Check that its summary covers both files before accepting the work. If it misses a guide, ask it to read that exact path. Explicitly reading the files makes this activity usable across coding agents; it is not a test of automatic instruction discovery.

Run `git status --short` to see changed and new files. Read the changed lines in your editor's diff view or with `git diff`. Open the new `src/order_total/AGENTS.md` directly too: plain `git diff` does not display untracked files. Then review the test results:

- Did the function keep its name and parameters?
- Are `Decimal` and the final rounding intact?
- Do the new and existing tests pass?
- Did the agent report what it changed and checked?

If you find a problem, look for missing or unclear guidance and ask for the needed correction. If the agent is still working at the end of the block, stop the run and confirm it has stopped before continuing. Use a written plan for the final step if needed, and return to the code review afterward.

### 11–15 minutes: revise the rule, then try an approved change

Make sure the previous run has finished or stopped. Read the starter rule about public functions alongside the maintainer's brief. Rewrite it to explain what ordinary fixes preserve and what an approved interface change needs to account for. Save the file, and keep the original sentence and your revision in your notes with a short reason for the change.

Start a **new conversation** in **m04-work** and give it this request:

> Read `AGENTS.md` and `src/order_total/AGENTS.md`. Name both files and briefly summarize the relevant rules. The maintainer has approved renaming `calculate_order_total` to `order_total`. Give me a short plan and explain how the instructions affect it. Leave every file unchanged.

Check the plan against the revised guidance. It should account for `demo.py` and the tests that call the function, while preserving the arithmetic and rounding requirements. If the plan misses something, identify the relevant instruction and clarify the plan. You can also check `git status --short` and the diff to confirm this planning step added no changes.

A useful revision expresses both ordinary fixes and approved changes clearly. It does not require the agent to make a mistake first. If the agent is unavailable or slow, write the rename plan yourself and use the same checks.

### What to keep

- Your root and local `AGENTS.md` files.
- The quantity-validation change and test results, or a written plan if you used the fallback.
- A short rename plan that accounts for affected callers and tests.
- The original public-function rule, your revision, and why you changed it.

No push or pull request is required. Keep the work in your own copy.

### If setup or agent access is unavailable

Read the starter files on GitHub. Draft the two guides and a short plan for each task in your notes, then revise the public-function rule. You can pair with a learner whose copy is running. The slide's timings are a guide, so move on to the revision step even if the implementation needs more time.

### Earlier workbook: instruction tracing

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
