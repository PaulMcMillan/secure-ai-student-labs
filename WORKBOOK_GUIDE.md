# Workbook exercise guide

Use these directions for the practical activities in the current slide sequence. Each activity names its starting files, steps, checks, deliverables, and fallback. Use your own notes for the evidence record; the Word workbook is optional for these practical directions. Lecture explanations, knowledge questions, and formal assessment remain in the course materials. M03 follows the approved offline adaptation and explicitly lists the missing steps to skip.

## Before starting

- Use Python 3.11+ and a disposable copy or your own branch.
- Run each code-block line separately from the repository root unless a `cd` is shown.
- For coding/evidence activities, keep a note with: task and scope; acceptance criteria; environment/authority; files consulted; commands and actual output; review; unresolved risks; and completion/stop decision. M00 is optional study practice and M01 is a setup check.
- A reference record is an example. Do not submit its claims as evidence that you performed the work.
- The ZIP contains source but no Git history. Clone if you need `git diff`, branches, or an immutable starting commit; otherwise keep an untouched copy for comparison and label Git checks “not run.”
- From the repository root, create a folder for your own notes and copied records:

```sh
python -c "from pathlib import Path; Path('student-work').mkdir(exist_ok=True)"
```

Use your editor/file manager to copy the named starter to the named destination before running a checker on your record. `student-work/` is ignored by Git. A checker returning `1` for an incomplete record is expected; preserve its issues and record a stop if you cannot resolve them in time. The supplied JSON contracts describe synthetic workflows: retain their field names and clearly distinguish scenario claims from actions you actually performed.

## M00 — Foundations and context budgeting

**Optional: choose one activity, about 15–25 minutes.** This follows revised slide **M00 S024**, replacing the older all-in-one homework. Keep a small table, an annotated diagram, or a one-page plan. No live model/API call is required.

### Option A: inspect tokens

Use this option only if an approved local tokenizer is already available. Otherwise **skip it and choose B or C**; no tokenizer is bundled or required for the other activities.

1. Record the tokenizer library/version and encoding (the slide examples use `o200k_base`).
2. Compare these exact strings: `Helping`, `helping`, `Extraordinary`, and ` extraordinary`. The last begins with one space.
3. Make a table with exact input (mark spaces visibly), token pieces, IDs, count, and decoded text. Verify that decoding the complete sequence restores the original text.
4. Explain how a fixed vocabulary and encoding rules produce the split, and distinguish vocabulary construction from encoding a request. Results from different tokenizer versions/encodings need not match.

Keep the table and two or three explanatory sentences. If you only inspected examples without running a tokenizer, label the values “provided example; not independently run.”

### Option B: trace the model

Draw this generation path: token IDs, embeddings plus position information, Transformer layers, vocabulary scores (logits), probabilities, token selection, append the selected token, and repeat. Mark the stopping signal or output limit.

Expand one Transformer block to show normalization, self-attention, queries/keys/values, residual additions, and the feed-forward network. Label whether you drew a decoder-only or encoder–decoder model; include cross-attention only for the latter. Explain that attention weights combine internal representations, while output probabilities guide selection of the next token. Add why known training positions can be processed in parallel while ordinary generation adds tokens sequentially.

Keep the annotated diagram. Check that residual paths bypass their sublayers, future tokens are masked in causal attention, and you have not drawn a token ID as an attention output.

### Option C: plan the context

Use these **exercise assumptions**, not a claim about your account's current limits: total context 1,050,000 tokens, separate input cap 922,000, generated-output cap 128,000. Reasoning uses the generated allowance rather than a second output budget.

You are investigating a bug in a repository. Your initial complete input, including instructions and tool definitions, is 800,000 tokens. After one step you retain another 2,000 tokens and receive 40,000 tokens of tool results. After the next, retain another 5,000 and receive 50,000 more.

1. Calculate input used and remaining input headroom at all three points. Check both the separate input cap and total context/output constraint.
2. Explain why requesting less output does not remove the input cap, and reserve room for a future tool result.
3. List the code/tests/log excerpts needed now, material to retrieve later, and decisions to save across sessions.
4. Draft a compaction note preserving the task, constraints, decisions and reasons, exact unresolved errors, approvals, and links to original evidence.
5. Name one access check before returning a file to the model and one application-enforced tool permission. Explain why caching does not enlarge the context window.

Keep your arithmetic and one-page plan. State assumptions and distinguish measurements from estimates. The optional [foundations evidence checker](examples/secure-ai-foundations/README.md) is separate practice, not a substitute for your chosen activity.

## M01 — Hands-on setup

**Current activity: hands-on setup, revised M01 S006.** Connect the course-approved coding agent, open the intended project, make one small edit, and run a check in the same environment. The older sanitized-evidence/configuration lab is optional practice below.

### Get connected

1. Follow the instructor's installation or connection steps and sign in through the normal product/connection flow. Do not paste credentials into a conversation.
2. Download this repository, then copy [examples/module-01/hands-on](examples/module-01/hands-on/README.md) to your own writable folder, such as `m01-work`. Open that folder in your agent.
3. Confirm the intended local or remote checkout, where commands execute, and the account/connection used. A remote command checks the code on that host, so ensure that host has your practice copy.
4. Find the permission controls and use the settings agreed for the exercise. Identify project instructions/settings and any hooks before trusting or enabling them. You do not need to install a hook, plugin, or MCP server.

### Try the small task

Ask the agent to find `check_setup.py`, read it, and explain what it checks. From **m01-work**, run:

```sh
python check_setup.py
```

Expected starter result: “Practice edit pending” and exit `1`. Give the agent this request:

> Change only practice.txt from status: pending to status: ready. Run python check_setup.py in this same checkout and report the changed line and result.

Inspect `practice.txt` and the check output yourself. Expected: `PASS: this checkout contains the practice edit and Python ran the check.` with exit `0`. Use `python3` or `py -3` if that is your Python command. Leave `check_setup.py` unchanged.

### Before moving on

Confirm the agent can read and edit the intended project and run its tools. If it edits successfully but the check cannot run, investigate missing Python, the wrong directory, or a different remote checkout with the instructor. Keep or revert your practice edit as directed; restoring `status: pending` resets the example. The pass proves that this checkout contains the edit and the check ran; it does not certify sandbox or account policy.

If setup is unavailable, pair with a learner and observe the steps, or diagnose the issue with the instructor. Mark unrun work “not run.” No formal evidence packet is required for this revised setup activity.

### Optional: earlier workbook configuration review

Run from the **student repository root**, not m01-work:

```sh
python examples/module-01/setup-check/setup_check.py
python examples/module-01/setup-check/config_guard.py examples/module-01/setup-check/configs/safe-project.toml
python examples/module-01/setup-check/config_guard.py examples/module-01/setup-check/configs/safe-permission-profile.toml
python examples/module-01/setup-check/config_guard.py examples/module-01/setup-check/configs/unsafe-project.toml
python examples/module-01/setup-check/config_guard.py examples/module-01/setup-check/configs/unsafe-mixed-permissions.toml
python -m unittest discover -s examples/module-01/setup-check/tests -v
```

Safe fixtures exit `0`, unsafe fixtures exit `1`, and 11 tests pass. Inspect the examples without copying them into live configuration. [Workload identity](examples/module-01/workload-identity/README.md) is additional optional practice.

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

**Time: 15 minutes. Slides M05 S011–S012.** A pricing threshold changes while the team is planning. Your task is to route that correction, preserve authority, and write a bounded plan. This is an offline planning activity; skip live model calls and do not implement the pricing change.

### 0–2 minutes: inspect the scenario

Read [task.json](examples/module-05/steering-plan/task.json) and compare [structured.json](examples/module-05/steering-plan/plans/structured.json) with [unsafe.json](examples/module-05/steering-plan/plans/unsafe.json). Their paths describe a proposed pricing task; no missing production repository needs to be created.

```sh
python examples/module-05/steering-plan/steering_check.py examples/module-05/steering-plan/task.json examples/module-05/steering-plan/plans/structured.json
python examples/module-05/steering-plan/steering_check.py examples/module-05/steering-plan/task.json examples/module-05/steering-plan/plans/unsafe.json
```

Structured exits `0`; unsafe exits `1`. Explain at least one skipped phase and one authority/scope problem in the unsafe record.

### 2–6 minutes: write the contracts

In your notes, make one row each for Explore, Plan, Implement, Test, and Review. Each row needs a deliverable, allowed paths, unchanged constraints, validation, stopping condition, and exact exit-evidence name from `task.json`. Implementation cannot begin until the plan gate is approved. Preserve the supplied model/authority/evaluation contract when discussing a model change.

### 6–9 minutes: route the correction

For a concrete classroom example, assume the approved threshold changes from 100 to 200 units before implementation. Record those as scenario assumptions. Draft the message you would send to steer the task: identify the changed requirement, retain file/permission boundaries, revise boundary-test cases, and require reapproval before implementation. Explain why a side conversation alone would not update the active plan, when separate work is appropriate, and what uncertainty would make you stop.

### 9–13 minutes: bound execution

Use [plan-mode-template.md](examples/module-05/prompt-loop/plan-mode-template.md) and [bounded-loop-template.md](examples/module-05/prompt-loop/bounded-loop-template.md) to write a task contract with measurable completion, maximum attempts, tool calls, elapsed time, token/cost ceiling, and escalation. Choose explicit finite values as a proposal. At each checkpoint record hypothesis, smallest action, result/evidence, remaining budget, and continue/re-plan/stop decision. You are writing the contract, not starting an autonomous loop.

### 13–15 minutes: check and hand off

```sh
python -m unittest discover -s examples/module-05/steering-plan/tests -v
```

Expected: 8 tests pass; older workbook text says seven. Keep the two checker reports, five phase contracts, routing rationale, steer message, and bounded execution contract. A peer should be able to identify what changed, what stayed authorized, and exactly when work must stop. If Python is unavailable, do the comparison in notes and mark the checker/tests “not run.”

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

**Time: 17 minutes. Slide M07 S015.** Implement the inventory reservation work item and hand off evidence that another person can review.

Use a disposable copy of the repository. Read the starter [AGENTS.md](examples/module-07/change-workflow/starter-repo/AGENTS.md), [WORK_ITEM.md](examples/module-07/change-workflow/starter-repo/WORK_ITEM.md), `src/inventory.py`, and `tests/test_inventory.py`.

### 0–4 minutes: contract and baseline

Record your starting commit or identify the untouched ZIP copy. Permit changes only to the starter's `src/inventory.py` and `tests/test_inventory.py`. Plan two increments: a reproducing test, then the smallest implementation. Write four acceptance cases: positive subtraction, insufficient-stock rejection, zero rejection, and negative rejection. Preserve the function signature and existing exception behavior.

Give execution a 10-minute budget and a minute-10 checkpoint. Keep one writer. Choose a disposable local copy or an isolated worktree and explain your choice. Optional side conversations or reviewers do not receive write authority.

```sh
cd examples/module-07/change-workflow/starter-repo
python -m unittest discover -s tests -v
cd ../../../..
```

Two baseline tests pass. Stop on an unexpected baseline failure.

### 4–10 minutes: implement

Add separate tests for zero and negative requests, run them to show failure on the starter, then add the guard. Rerun the same test command from inside `starter-repo`. Four tests should now pass. Stop at the budget boundary and record incomplete work if needed. Compare the supplied solution only after your attempt.

### 10–15 minutes: review and remediate

Review the changed lines and all four cases. Check the return value, `ValueError` behavior, unchanged interface, and absence of unrelated edits. Ask a peer or a read-only reviewer to inspect the diff. Correct evidenced problems and rerun the affected tests. A solo review must be labeled as such.

### 15–17 minutes: hand off

Keep the contract, base/copy identity, diff, exact test commands and results, review findings and decisions, skipped checks, remaining risk/budget, and stop reason. The reference evidence checker illustrates a complete handoff:

```sh
python examples/module-07/change-workflow/workflow_check.py examples/module-07/change-workflow/task.json examples/module-07/change-workflow/evidence/complete.json
python examples/module-07/change-workflow/workflow_check.py examples/module-07/change-workflow/task.json examples/module-07/change-workflow/evidence/unsafe.json
python -m unittest discover -s examples/module-07/change-workflow/tests -v
```

Complete exits `0`, unsafe exits `1`, and 10 checker tests pass. These records do not attest to your implementation. Keep your own real output. Without execution access, write the plan/test cases and critique the reference diff, labeling implementation and tests “not run.”

## M08 — MCP integration dossier

**Time: 19 minutes. Slide M08 S016.** Review the [stateless STDIO fixture](examples/module-08/stateless-mcp/README.md) as a proposed integration. It runs locally with static data and no credentials. Use its pinned course protocol version for this exercise; no live client configuration is required.

### 0–4 minutes: map the boundary

Read `client.py`, `server.py`, and `risk-dossier.json`. Draw the host/client, Python child process, STDIO transport, local identity, static data, one pinned tool, and request/result boundaries. Mark self-reported client metadata, tool descriptions, and returned content as untrusted. List the absent downstream services.

### 4–9 minutes: trace the requests

```sh
python examples/module-08/stateless-mcp/client.py
```

Identify independent discovery, tool-list, and tool-call responses. Expect three responses and one `lookup_policy` tool. Find per-request protocol/client-capability metadata, server metadata, `resultType`, schema validation, and cache hints in the code/output. Explain that the server provides discovery while a client may choose not to invoke it. This course fixture has no session handshake.

### 9–14 minutes: prove four controls

Copy `risk-dossier.json` to `student-work/m08-dossier.json` using your editor/file manager. Explain each control in your own words and cite the handler or test that supplies evidence:

| Control | Evidence to provide |
| --- | --- |
| Per-request protocol and capability checks | Where missing/unsupported metadata is rejected |
| Pinned tool inventory | Where names other than `lookup_policy` are rejected |
| Issuer and token audience | Explicitly not applicable to this credential-free fixture; describe the check a protected remote service would require |
| Side-effect approval | Explain why this static read has no write approval; describe preview, approval, idempotency, and recovery needed before adding a write |

Keep the owner, audit, identity boundary, disablement, and removal fields. An annotation or a passing dossier check alone is not enforcement.

### 14–19 minutes: validate and retire on paper

```sh
python examples/module-08/stateless-mcp/dossier_check.py student-work/m08-dossier.json
python -m unittest discover -s examples/module-08/stateless-mcp/tests -v
```

A complete dossier exits `0`; 12 tests pass, including invalid metadata/version and unknown-tool cases. Record the rejection evidence. Write how an owner would disable access, verify tool absence, remove configuration/distribution, revoke any future credentials, and retain audit evidence. **Skip registering a live server, remote authentication, and real credential revocation.** Those are design notes for this fixture, not actions to perform.

Keep the boundary map, your dossier, client/test output, residual risks, and retirement plan. If Python is unavailable, trace the supplied code in notes and mark checks “not run.” Optional follow-on: [MCP security](examples/module-08/mcp-security/README.md) or [RAG bridge](examples/module-08/rag-mcp-bridge/README.md). The legacy `local-mcp` example is not the core activity.

## M09 — Tool selection

**Time: 8 minutes. Slides M09 S009 and S012.** A team proposes letting two coding agents edit the same checkout at once. Replace that with one implementation owner followed by a distinct read-only architecture review. Use the offline records; live Claude access is unnecessary.

1. **0–2 minutes — decide:** compare [unsafe-dual-edit.json](examples/module-09/tool-selection/scenarios/unsafe-dual-edit.json) and [bounded-sequence.json](examples/module-09/tool-selection/scenarios/bounded-sequence.json). Name the required patch and the separate review deliverable. Explain why the proposed sequence serves this task.
2. **2–4 minutes — authority:** assign the implementation role write access and reviewer read access. Preserve one immutable base/patch reference and separate output names. Review the dated `product_baseline` as synthetic evidence. Its flags and `CLAUDE.md` text do not prove live controls are enabled.
3. **4–6 minutes — handoff:** copy `bounded-sequence.json` to `student-work/m09-handoff.json`. Write your own task-specific rationale and role purposes. For each role retain base, allowed paths, authority, inputs, output, validation, stop, and receiving owner. Make it clear that the writer stops before review begins. `abc1234` is a fictional scenario label, not a real checkout instruction.
4. **6–8 minutes — validate:** run:

```sh
python examples/module-09/tool-selection/decision.py student-work/m09-handoff.json
python examples/module-09/tool-selection/decision.py examples/module-09/tool-selection/scenarios/unsafe-dual-edit.json
python -m unittest discover -s examples/module-09/tool-selection/tests -v
```

Your complete record exits `0`, unsafe exits `1`, and 10 tests pass. Give a peer your handoff: they should be able to identify why each role exists, what it may change, and when it stops. Keep the record and reports. **Skip starting two agents, buying access, or changing live sandbox settings.** Without Python, review the records manually and mark execution “not run.”

## Shared RAG evidence for M10–M12.5

Keep `examples/rag-reference`, `examples/evidence/EV-RAG-01.json`, and `examples/rag_evidence_binding.py` together. The later checkers verify the observation and source hashes. Run the M03 ingest/query/eval commands to obtain your own functional output; `python scripts/validate_course.py` also reruns that behavior in a temporary directory.

M10, M11, and M12.5 consume the pre-staged observation. M12 additionally asks you to execute the RAG path and retain real output. Do not edit the shared corpus or evidence to make a checker pass. An evidence record passing its checker proves its structure and bindings, not a real approval or deployment. In M12/M12.5, the fixture `runtime` flags describe actions by the offline checker and remain false. Keep your own shell/test execution evidence separately in the validation entries and notes.

## M10 — Lifecycle gates

**Time: 15 minutes. Slide M10 S015.** Replace this unsafe proposal: “Ingest the latest documents, let the model pick the tenant filter, retry until answers look right, approve its own result, and promote the index.” Your deliverable is a reproducible synthetic lifecycle contract.

Read [task.json](examples/module-10/lifecycle-gates/task.json). Copy [evidence/starter.json](examples/module-10/lifecycle-gates/evidence/starter.json) to `student-work/m10-release.json`. Use the complete record as a schema/reference, keeping all fictional approvals and releases labeled as scenario data.

1. **0–3 minutes — lifecycle:** list the ten required states in order. For each, record owner, identity/authority, required evidence, pass condition, and who acts on failure. Track corpus, index, configuration, evaluator, and release separately.
2. **3–7 minutes — gates:** map ingestion, retrieval quality, citation support, abstention, tenant access, injection, freshness/deletion, cost, and diff checks to the test gate. Keep authorization outside the model. Bind the supplied EV-RAG observation and its full digests.
3. **7–10 minutes — approval/recovery:** separate implementer, reviewer, approver, release, and recovery roles. Explain why changes to artifacts or authority invalidate prior approval. Distinguish retryable failure from quarantine/escalation.
4. **10–13 minutes — operation:** name monitoring/alert owners, the proposed SLO and cost ceiling, and rollback/reindex triggers. Keep raw sensitive content out of telemetry. Use scenario values from the reference; do not label simulated latency/cost as locally measured.
5. **13–15 minutes — check:** run the supplied comparisons, then your record:

```sh
python examples/module-10/lifecycle-gates/workflow_check.py examples/module-10/lifecycle-gates/task.json examples/module-10/lifecycle-gates/evidence/complete.json
python examples/module-10/lifecycle-gates/workflow_check.py examples/module-10/lifecycle-gates/task.json examples/module-10/lifecycle-gates/evidence/unsafe.json
python examples/module-10/lifecycle-gates/workflow_check.py examples/module-10/lifecycle-gates/task.json student-work/m10-release.json
python -m unittest discover -s examples/module-10/lifecycle-gates/tests -v
```

Complete exits `0`, unsafe/incomplete exits `1`, and 12 tests pass. Repair your record using the reported issues, without weakening the checker. If time expires, keep the incomplete result and name the next owner/action. Keep the record, lifecycle/gate table, reports, recovery plan, and stop decision. **Skip real deployment, cloud monitoring, and permission changes.** Without Python, critique the supplied records and label the checks “not run.”

## M11 — Parallel work and merge safety

**Time: 13 minutes. Slide M11 S015.** Plan separate retrieval-quality and security evaluations of one RAG release, independent review, and one integration decision. You are reviewing records, not launching agents or merging real branches.

Read [task.json](examples/module-11/task-merge-safety/task.json), copy [evidence/starter.json](examples/module-11/task-merge-safety/evidence/starter.json) to `student-work/m11-integration.json`, and consult the complete record for its schema.

1. **0–3 minutes — graph:** draw the six task IDs and four waves from the reference. Show dependencies and explain why each dependency finishes before its consumer starts. Stay within the declared maximum of two parallel workers.
2. **3–6 minutes — operations:** use the scenario base `abc1234` consistently; it is fictional. Record inherited permissions, root and per-task budgets, concurrency, steer/cancel owner, attempts/time limits, and stops. Keep inventories and reviewer read-only.
3. **6–9 minutes — evidence ownership:** give quality and security workers distinct proposed outputs/worktrees. Bind both to the same EV-RAG artifact and corpus/index/configuration/evaluation digests. Assign retrieval/citation/abstention to quality and access/injection/freshness/deletion to security.
4. **9–11 minutes — integrate:** use a reviewer different from the author. Give the integrator the order, checks for compatible evidence, digest-mismatch rejection, conflict-resolution record, monitoring/cost/provenance gates, and residual risk.
5. **11–13 minutes — check:** run:

```sh
python examples/module-11/task-merge-safety/merge_check.py examples/module-11/task-merge-safety/task.json examples/module-11/task-merge-safety/evidence/complete.json
python examples/module-11/task-merge-safety/merge_check.py examples/module-11/task-merge-safety/task.json examples/module-11/task-merge-safety/evidence/unsafe.json
python examples/module-11/task-merge-safety/merge_check.py examples/module-11/task-merge-safety/task.json student-work/m11-integration.json
python -m unittest discover -s examples/module-11/task-merge-safety/tests -v
```

Complete exits `0`, unsafe/incomplete exits `1`, and 12 tests pass. Keep your graph/waves, role and integration contracts, reports, and stop decision. If incomplete, list unresolved issues rather than claiming a merge succeeded. **Skip actual agent spawning, worktree creation, Git merges, and deployment.** A written reference critique is the fallback when execution is unavailable.

## M12 — Release-evidence capstone

**Time: 26 minutes. Slides M12 S003 and S011–S014.** Add an explanation to the pricing function, preserve its existing totals, and defend the change with code and offline RAG evidence.

Use a disposable copy/branch of the whole collection so the shared RAG paths remain available. Read [task.json](examples/module-12/release-evidence/task.json), `starter/pricing.py`, `starter/tests/test_pricing.py`, and [evidence/starter.json](examples/module-12/release-evidence/evidence/starter.json). Copy that evidence starter to `student-work/m12-capstone.json`; keep `student-work/m12-rag-report.json` for your observed RAG evaluation.

### 0–4 minutes: contract

Record goal, start commit or ZIP snapshot, assumptions, instructions consulted, tools/permissions, time/iteration budget, escalation, validation, review, and stop. The task's `pricing.py` and `tests/test_pricing.py` refer to the files under `starter/`. Its two evidence outputs map to your `student-work` records. Keep these mappings explicit in your notes and use the task's relative names in the synthetic contract.

Acceptance:

- Preserve `quote_total`'s standard and partner totals, including its 10% partner discount and two-decimal rounding.
- Add `explain_quote(subtotal, segment="standard")`, returning `subtotal`, `discount_rate`, `total`, and `reason`. Use a clear reason such as `standard rate` or `partner discount`.
- Reject negative/non-numeric subtotals (including booleans) and unknown segments with `ValueError`, preserving the starter's validation.
- Test both explanation paths and invalid input, and retain the two baseline total tests.

```sh
python -m unittest discover -s examples/module-12/release-evidence/starter/tests -v
```

Expected: two baseline tests pass. Stop on unexpected baseline failure.

### 4–12 minutes: implement and prove

Add your focused tests, show the new behavior failing before implementation, then make the smallest change inside `starter/pricing.py` and `starter/tests/test_pricing.py`. Rerun the command above. The reference solution has five test methods; your tests must cover all acceptance behaviors even if organized differently. Inspect the solution only after attempting the work.

### 12–18 minutes: assemble RAG and code evidence

Run the [M03 ingest and authorized-query commands](#m03--authorized-rag-trace), then:

```sh
python examples/rag-reference/rag.py eval --index examples/rag-reference/build/index.json --cases examples/rag-reference/evals/cases.json --telemetry examples/rag-reference/build/telemetry.jsonl --report student-work/m12-rag-report.json
```

Expect 7 source documents, 5 indexed documents/chunks, 8/8 evaluation cases, and ten metrics at 1.0. Link the supplied EV-RAG observation and full digests plus your actual saved output. The checker independently verifies file bindings. Do not modify the shared RAG source/corpus to pass a gate. Mark hosted latency, provider cost, scale, and live deployment/recovery **skipped — not supplied by this lab**.

Complete the eleven `required_domains` in `task.json`: instructions, context, decision, cost, tools, workflow, security, RAG, validation, review, and release. Give evidence entries unique identifiers and real file/output references for work you performed. Label inherited reference/scenario data distinctly. If an actual review or observation is missing, record it as unresolved instead of inventing a pass.

### 18–22 minutes: independent review

Exchange a named diff and RAG report with a peer. The reviewer checks behavior, tests, scope, authorization/citations, monitoring/cost assumptions, and provenance without editing your files. Record findings, your decisions, and any rerun checks. If no independent reviewer is available, record the review gap and choose a safe-stop handoff.

### 22–26 minutes: release decision and defense

Explain who owns the result, which gates passed, what remains uncertain, how to undo your code change, and how to rebuild a trusted RAG index. This is a classroom release decision; **do not deploy**. Give a two-minute defense to a peer, then listen to theirs: task/boundary, main decision, strongest code/RAG evidence, residual risk, and recovery.

```sh
python examples/module-12/release-evidence/evidence_check.py examples/module-12/release-evidence/task.json examples/module-12/release-evidence/evidence/complete.json
python examples/module-12/release-evidence/evidence_check.py examples/module-12/release-evidence/task.json examples/module-12/release-evidence/evidence/unsafe.json
python examples/module-12/release-evidence/evidence_check.py examples/module-12/release-evidence/task.json student-work/m12-capstone.json
python -m unittest discover -s examples/module-12/release-evidence/tests -v
```

Complete exits `0`, unsafe/incomplete exits `1`, and 13 checker tests pass. Use issues to find missing evidence; an honestly incomplete record and explicit stop are preferable to fabricated validation. Keep the contract, diff, code/RAG results, evidence record, review, and decision. If tools are unavailable, produce a written critique of the reference and mark execution “not run.”

## M12.5 — Optional practice check

**Time: 17 minutes. Slides M12.5 S014–S015.** Turn an unsafe “answers looked right, enable every tool, retry indefinitely, self-review, then automate” proposal into a bounded operating packet for the existing RAG fixture.

Read [task.json](examples/module-12-5/practice-check/task.json). Copy [records/starter.json](examples/module-12-5/practice-check/records/starter.json) to `student-work/m125-packet.json`. Inspect the complete record for schema and the unsafe record for failure cases. Use the supplied EV-RAG observation; no new retrieval system or plugin is required.

1. **0–4 minutes — frame:** write the goal, context references, allowed/excluded paths, immutable base/snapshot, assumptions, unknowns, four done conditions, and stop. Separate one-task instructions from reusable project guidance.
2. **4–8 minutes — bound:** describe Explore, Plan, Implement, Test, and Review, with deliverables and validation. Identify risk and two decision points. Keep filesystem/shell/local-RAG authority, no external tools, and an empty plugin inventory. Declare finite minutes/iterations and escalation. Do not change model authority when discussing escalation.
3. **8–14 minutes — prove:** complete the eight named checks in `task.json`, binding RAG source/observation digests, ingest counts, eight categories, ten metrics, monitoring owner/alert route, and recovery. Reference actual outputs when run, clearly label supplied scenario evidence, and record unobserved hosted cost/latency as a gap. Get a read-only critique from a different reviewer, or record that review is outstanding.
4. **14–17 minutes — improve and stop:** keep first-use guidance at task scope. Write when repeated evidence would justify reuse, one measurable improvement with an owner/review date, and an explicit stop/next-owner record. Give all twelve practices unique evidence references. Run:

```sh
python examples/module-12-5/practice-check/practice_check.py examples/module-12-5/practice-check/task.json examples/module-12-5/practice-check/records/complete.json
python examples/module-12-5/practice-check/practice_check.py examples/module-12-5/practice-check/task.json examples/module-12-5/practice-check/records/unsafe.json
python examples/module-12-5/practice-check/practice_check.py examples/module-12-5/practice-check/task.json student-work/m125-packet.json
python -m unittest discover -s examples/module-12-5/practice-check/tests -v
```

Complete exits `0` with twelve practices plus the separate RAG operations gate; unsafe/incomplete exits `1`; 14 tests pass. Keep your packet, reports, review/gaps, reuse decision, and retrospective. **Skip installing plugins, scheduling automation, production checks, and deployment.** Without Python, critique the records in notes and mark the checks “not run.”

## Supplemental scenario numbering

The [security task range](examples/security-task-range/README.md) retains its original storyline IDs: its M01 boundary-mapping episode fits current workbook M02, and its M02 setup episode fits current workbook M01. Treat these as scenario identifiers, not repository directory names. The remaining numbered scenarios support their corresponding modules.

See the [repository README](README.md#supplemental-exercises) for all other optional fixtures. Exact CLI working directories are stated in each fixture README.
