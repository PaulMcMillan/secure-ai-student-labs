# Workbook exercise guide

Use these directions for the practical activities in the current slide sequence. Each activity names its starting files, steps, checks, deliverables, and fallback. Use your own notes for the evidence record; the Word workbook is optional for these practical directions. Lecture explanations, knowledge questions, and formal assessment remain in the course materials. M03 follows the approved offline adaptation and explicitly lists the missing steps to skip. The revised M04 and M06 directions replace those sections in older workbooks.

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

For M04, M07, and M12, keep one terminal at the **lab collection root** and a second terminal in the prepared working project. Each activity names where to run its commands. Return to the lab terminal when a module ends.

M06 and the prepared coding activities save results in `student-results/` at the lab collection root. Create it in your editor or run `python -c "from pathlib import Path; Path('student-results').mkdir(exist_ok=True)"`. Both `student-work/` and `student-results/` are Git-ignored. Follow the destination named by each activity and keep the supplied fixtures unchanged.

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

**Goal:** give an agent project knowledge it cannot learn from the code, then verify that the implementation uses it. Allow about 15 minutes after preparation: 2 minutes for the brief and 13 minutes for the work.

Read these directions yourself. Keep the workbook and acceptance checker outside the agent's working project. Give the agent only the task prompts below and the guides you write.

### Before the timer: prepare a fresh project

From the **secure-ai-student-labs root**, run:

```sh
python scripts/prepare_m04.py ../m04-work
```

Use a new destination name if `m04-work` already exists. Earlier copies may contain a different exercise or your previous changes. Open the new folder as the project in your coding agent.

From **m04-work**, run:

```sh
python -m unittest discover -s tests -v
python demo.py
```

Expected baseline: **4 passing tests** and `Order total: 13.50`. The new `delivery_fee` function raises `NotImplementedError`; the existing calculator and its tests work. No extra packages or AITrainer files are needed. Use `python3` or `py -3` if that is your Python command.

The preparation script copies only seven starter files and creates a local Git baseline when Git is available. It does not copy this workbook, the acceptance checker, or any solution.

```text
m04-work/
├── AGENTS.md                   basic starter instructions
├── demo.py                     an existing calculator caller
├── src/order_total/pricing.py  calculator and delivery_fee stub
└── tests/test_pricing.py       existing calculator checks
```

### 0–2 minutes: the maintainer's brief

The business has decided this delivery policy. It is deliberately absent from the starter code:

- The delivery fee is **$5 for a subtotal below $50**.
- Delivery is **free at $50 or more**, including exactly $50.
- `delivery_fee(subtotal)` returns **the fee only**, as a `Decimal`.
- Inputs are valid, nonnegative `Decimal` amounts already rounded to cents. Input validation and additional delivery options are outside this task.

Keep the existing `calculate_order_total` behavior, including `Decimal` arithmetic and `ROUND_HALF_UP` rounding. Use only the standard library. Review the diff and report test results when finishing.

The public policy promises free delivery starting at $50, so the exact boundary matters. Your guides should make that decision clear to someone working on the calculator later.

### 2–4 minutes: find the missing knowledge

Before writing the guides, start a conversation in **m04-work** and ask:

> Read the code for `delivery_fee`. What project policy do you need before you can implement it? Do not invent a policy or change files.

Save one question the code could not answer. An agent asking for the price or free-delivery threshold is behaving usefully. If it proposes a default, check whether it can point to a project source for that value. Do not treat a guess as an established policy.

Leave the files unchanged during this step. Keep the brief in your own notes for the next part; do not paste the whole workbook into the chat.

### 4–8 minutes: write the guides yourself

1. Improve the root `AGENTS.md`: add a small file map, the test command with its working directory, the standard-library requirement, preservation of existing calculator behavior, and review/test reporting.
2. Create `src/order_total/AGENTS.md`: record the delivery policy, the input and return contract, and the arithmetic/rounding requirements that apply to this code. Make the exactly-$50 case unambiguous.

A few clear sentences are enough. Use the root guide for shared workflow and the local guide for the calculator's policy. Identify the sentence that answers the question you saved in the previous step.

### 8–15 minutes: implement and check the policy

Start a **fresh conversation** in **m04-work**, then give the agent this request:

> Read `AGENTS.md` and `src/order_total/AGENTS.md`. Briefly state the project policy you found and where it is recorded. Implement `delivery_fee(subtotal)` from that policy. Add tests and run the test suite. Preserve the existing calculator behavior.

Notice that the prompt supplies no fee or threshold. Check whether the agent found those facts in your guide. If it misses a file, ask it to read the exact path.

Review the implementation, the new tests, and both guides. Use `git status --short` to include new files in the review; `git diff` does not display untracked files. Run the project's tests from **m04-work**:

```sh
python -m unittest discover -s tests -v
```

Then switch your terminal back to the **secure-ai-student-labs root** and run the independent acceptance check yourself:

```sh
python scripts/check_m04.py ../m04-work
```

Use your actual working-folder name if you chose a different one. Keep this checker outside the agent's project. It checks the implementation against the workbook policy, independently of the tests the agent wrote.

| Subtotal | Expected delivery fee |
| --- | --- |
| $49.99 | $5.00 |
| $50.00 | $0.00 |
| $50.01 | $0.00 |

All returned amounts must be `Decimal`. The four original calculator behaviors must also remain correct. A completed implementation passes **7/7 acceptance checks**. Running the checker on the untouched starter produces **4/7**, because delivery is not implemented yet.

Find the sentence in your local guide that decides the exactly-$50 case. If that sentence is ambiguous, clarify it and ask the agent to reread the guide and fix the behavior. If the guide is already clear but the implementation is wrong, ask for a code correction. Rerun the checks after a change.

If everything already passes, keep the sentence and the boundary results as your evidence. You do not need to introduce a bad rule or manufacture a revision.

### What to keep

- One missing-policy question and the guide sentence that answers it.
- Your root and local `AGENTS.md` files.
- The implementation, test results, and acceptance-check output.
- One ambiguity you clarified, or the wording that already made the boundary clear.

No push or pull request is required. Keep your work in your own copy.

### If the agent is slow or unavailable

Stop any unfinished run before changing instructions or moving on. Pair with another learner, or write the two guides and a short implementation plan yourself. Work through the three boundary cases in writing. That still demonstrates the missing knowledge, where you put it, and how you would check its effect; it does not count as a completed implementation.

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

Use the terminal at the **lab collection root**. Read [task.json](examples/module-05/steering-plan/task.json) and compare [structured.json](examples/module-05/steering-plan/plans/structured.json) with [unsafe.json](examples/module-05/steering-plan/plans/unsafe.json). Their paths describe a proposed pricing task; no missing production repository needs to be created.

```sh
python examples/module-05/steering-plan/steering_check.py examples/module-05/steering-plan/task.json examples/module-05/steering-plan/plans/structured.json
python examples/module-05/steering-plan/steering_check.py examples/module-05/steering-plan/task.json examples/module-05/steering-plan/plans/unsafe.json
```

Structured exits `0`; unsafe exits `1`. Explain at least one skipped phase and one authority/scope problem in the unsafe record.

### 2–6 minutes: write the contracts

In your notes, make one row each for Explore, Plan, Implement, Test, and Review. Each row needs a deliverable, allowed paths, unchanged constraints, validation, stopping condition, and exact exit-evidence name from `task.json`. Implementation cannot begin until the plan gate is approved. Preserve the supplied model/authority/evaluation contract when discussing a model change.

### 6–9 minutes: route the correction

The initial plan gives a 10% discount when the subtotal is at least $100. The maintainer corrects the requirement: the threshold is **at least $150**, with the rate still 10%. Draft the steer message, preserve the public API, dependencies, allowed paths, and budget, and require reapproval before implementation. Revise the boundary cases: $149.99 gets no discount; $150.00 and $150.01 get 10%. Name the earlier expectations that must change. Explain why a side conversation alone would not update the active plan, when separate work is appropriate, and what uncertainty would make you stop.

Save your steer and contract as `student-results/m05-plan.md`. The pricing paths in `task.json` describe a scenario, so no implementation needs editing. The supplied checker validates phase records; check your written threshold correction against this brief yourself.

### 9–13 minutes: bound execution

Use [plan-mode-template.md](examples/module-05/prompt-loop/plan-mode-template.md) and [bounded-loop-template.md](examples/module-05/prompt-loop/bounded-loop-template.md) to write a task contract with measurable completion, maximum attempts, tool calls, elapsed time, token/cost ceiling, and escalation. Use at most two implementation attempts and a 15-minute execution budget. Propose explicit finite limits for tool calls and token/cost usage. At each checkpoint record hypothesis, smallest action, result/evidence, remaining budget, and continue/re-plan/stop decision. You are writing the contract, not starting an autonomous loop.

### 13–15 minutes: check and hand off

```sh
python -m unittest discover -s examples/module-05/steering-plan/tests -v
```

Expected: 8 tests pass; older workbook text says seven. Keep the two checker reports, five phase contracts, routing rationale, steer message, and bounded execution contract. A peer should be able to identify what changed, what stayed authorized, and exactly when work must stop. If Python is unavailable, do the comparison in notes and mark the checker/tests “not run.”

## M06 — Model choice and reasoning effort

**Time: 20 minutes in pairs; allow 30 minutes alone.** Follow [the M06 activity](examples/module-06/README.md), which replaces the earlier cost-decision lab.

Create a Codex project named **M06 — Model choice**. Select [examples/module-06/starter-repo](examples/module-06/starter-repo) in your existing student checkout as its only folder and working root. Keep the evidence unchanged. Save answers in `student-results/m06/` at the checkout root, outside the exercise folder.

- **9 minutes:** split the models with a partner. Run GPT-5.5 and GPT-6 Astra at each model's lowest and highest available effort. Use the same prompt in four fresh chats, with up to four minutes per run.
- **8 minutes:** check both reconstructed views, the diagnosis, and the proposed regression tests. Run the checker from the student checkout root for each saved answer:

```sh
python examples/module-06/check_answer.py student-results/m06/A.json
```

- **3 minutes:** compare effort settings within each model, then compare the models. Recommend a configuration using correctness, response time, and review work.

The checker verifies 22 balance and exception results. Students must also check that the diagnosis and regression expectations agree with the evidence. Correct totals can appear alongside an incorrect proposed test. Use the review guide after assessing the answers yourself.

**Follow-on — 8 minutes:** copy the GPT-5.5 low answer into the exercise folder as `earlier-answer.json`. In a fresh chat, have GPT-6 Astra at High effort review it using the [follow-on prompt](examples/module-06/README.md#follow-on-review). Give it the case evidence and earlier answer, then verify its corrections yourself. A saved live answer is available if needed. Keep the review and your verdict with your results, and move the answer out of the exercise folder afterward.

## M07 — Implement, test, review, hand off

**Time: 17 minutes. Slide M07 S015.** Implement the inventory reservation work item and hand off evidence that another person can review.

Complete setup before the activity. From the **lab collection root**, prepare a separate copy of the starter:

```sh
python scripts/prepare_coding_lab.py m07 ../m07-work
```

The helper refuses to overwrite a destination and creates a Git baseline and exercise branch when Git is available. Open the printed **m07-work** folder as the agent's project and use a second terminal there. Read its `AGENTS.md` and `WORK_ITEM.md`, plus `src/inventory.py` and `tests/test_inventory.py`.

### 0–4 minutes: contract and baseline

Record `git rev-parse HEAD` inside m07-work if Git is available. Otherwise identify the untouched starter and record the limitation. Permit changes only to the starter's `src/inventory.py` and `tests/test_inventory.py`. Plan two increments: a reproducing test, then the smallest implementation. Write four acceptance cases: positive subtraction, insufficient-stock rejection, zero rejection, and negative rejection. Preserve the function signature and existing exception behavior.

Give execution a 10-minute budget and a minute-10 checkpoint. Keep one writer. Work in the prepared m07-work copy. Optional side conversations or reviewers do not receive write authority.

Run **inside m07-work**:

```sh
python -m unittest discover -s tests -v
```

Two baseline tests pass. Stop on an unexpected baseline failure.

### 4–10 minutes: implement

Add separate tests for zero and negative requests, run them to show failure on the starter, then add the guard. Rerun the same test command from inside **m07-work**. Four tests should now pass. Stop at the budget boundary and record incomplete work if needed. Compare the supplied solution only after your attempt.

### 10–15 minutes: review and remediate

Run `git diff` and `git status --short` inside m07-work and review the changed lines and all four cases. Without Git, compare with the untouched starter in your editor. Check the return value, `ValueError` behavior, unchanged interface, and absence of unrelated edits. Ask a peer or a read-only reviewer to inspect the diff. Correct evidenced problems and rerun the affected tests. A solo review must be labeled as such.

### 15–17 minutes: hand off

Keep the contract, base/copy identity, diff, exact test commands and results, review findings and decisions, skipped checks, remaining risk/budget, and stop reason. Switch back to the **lab collection root** terminal. After your attempt, compare the supplied solution and its tests. The reference evidence checker illustrates a complete handoff:

```sh
python examples/module-07/change-workflow/workflow_check.py examples/module-07/change-workflow/task.json examples/module-07/change-workflow/evidence/complete.json
python examples/module-07/change-workflow/workflow_check.py examples/module-07/change-workflow/task.json examples/module-07/change-workflow/evidence/unsafe.json
python -m unittest discover -s examples/module-07/change-workflow/tests -v
```

Complete exits `0`, unsafe exits `1`, and 10 checker tests pass. These records do not attest to your implementation. Keep your own real output. Without execution access, write the plan/test cases and critique the reference diff, labeling implementation and tests “not run.”

Use the complete record's field structure to write `student-results/m07.json` with your own results. Save the earlier failing-test output separately; the record's `commands` list describes final acceptance checks. The checker uses a dated model allowlist in `task.json`. If your actual model is absent, record it honestly and retain the rejection for instructor review; do not substitute an unused model to pass. Check your record from the lab root:

```sh
python examples/module-07/change-workflow/workflow_check.py examples/module-07/change-workflow/task.json student-results/m07.json > student-results/m07-check.json
```

Open the report, correct supported omissions, and rerun. An incomplete record exits `1`; a supported complete record exits `0`. Keep unresolved issues with your submission.

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

**Time: 26 minutes. Slides M12 S003 and S011–S014.** Add a quote explanation, preserve the existing totals, and defend the change with code and offline RAG evidence. Complete project setup before the activity.

### Prepare your working project

From the **lab collection root**, run:

```sh
python scripts/prepare_coding_lab.py m12 ../m12-work
```

The helper copies the [starter](examples/module-12/release-evidence/starter), its `AGENTS.md` and `WORK_ITEM.md`, `task.json`, and a blank record at `evidence/capstone.json`. It creates a local Git baseline and `student/m12-exercise` branch, even when the lab collection came from a ZIP. It refuses to overwrite an existing destination. Open the printed **m12-work** path as the coding project and use a second terminal there.

Git is required for this capstone's final baseline/branch evidence. If unavailable, pair with someone who has it, or complete the code and written work while marking that gate incomplete. Never invent a starting commit. Keep the lab collection terminal open for the shared RAG and checker commands.

### 0–4 minutes: contract and baseline

Read [the function contract](examples/module-12/release-evidence/starter/WORK_ITEM.md) and the copied `AGENTS.md` and `task.json` before editing. `explain_quote(subtotal, segment="standard")` returns `subtotal`, `discount_rate`, `total`, and `reason`; the work item defines their exact values, rounding, invalid-input behavior, examples, and required checks. Preserve `quote_total`.

Record the goal, scope, assumptions, instructions consulted, tool permissions, time and iteration limits, escalation, validation, review, and stopping conditions. Keep the task’s paths relative to m12-work.

Run **inside m12-work**:

```sh
git status --short --branch
git rev-parse HEAD
python -m unittest discover -s tests -v
```

Save the baseline commit and output: **2 tests pass**. Stop on an unexpected baseline failure.

### 4–12 minutes: implement and prove

Add the work item's acceptance tests, retain their failure before implementation, implement the function, and rerun the same test command. Keep evidence outside the project in `student-results` or your workbook notes until you reference it in the allowed evidence files.

Still **inside m12-work**, review your final result:

```sh
python -m unittest discover -s tests -v
git diff -- pricing.py tests/test_pricing.py
git status --short
```

Check both explanation cases, rounding consistency, invalid inputs, and the unchanged valid totals. The number of your test methods may vary. Allowed edited paths are `pricing.py`, `tests/test_pricing.py`, `evidence/capstone.json`, and `evidence/rag-report.json`. Open new evidence files directly because plain `git diff` omits untracked files.

### 12–18 minutes: assemble RAG and code evidence

Switch to the **lab collection root** terminal. Run the [M03 ingest and authorized-query commands](#m03--authorized-rag-trace), then save the evaluation output:

```sh
python examples/rag-reference/rag.py eval --index examples/rag-reference/build/index.json --cases examples/rag-reference/evals/cases.json --telemetry examples/rag-reference/build/telemetry.jsonl --report student-results/m12-rag-output.json
```

Expect 7 source documents, 5 indexed documents/chunks, 8/8 evaluation cases, and ten metrics at 1.0. Keep the actual outputs and full digests. Keep the shared RAG source and corpus unchanged. Record hosted latency, provider cost, scale, and live deployment/recovery as unmeasured in this lab. In **m12-work**, create `evidence/rag-report.json` with the observed status, counts, index version, integrity digest, evaluation results, and references to those saved outputs. State that these paths are relative to the separate lab collection. Submit the referenced outputs with the report.

Fill in **m12-work/evidence/capstone.json**, using the supplied complete record to understand the field structure. Record your actual baseline SHA, branch, changed paths, and test/review evidence. For `baseline`, `focused`, and `regression`, reference your saved test runs. For `rag`, reference the M03 outputs. For `security`, document your input-validation tests and review of dependencies, data, and tool boundaries; for `diff`, reference your reviewed diff. Give each of the eleven domains a unique `EV-` identifier and map it to your actual evidence in your workbook notes.

### 18–22 minutes: independent review

Exchange the final diff and RAG report with a peer. Check behavior, tests, scope, authorization and citations, monitoring/cost assumptions, and provenance without editing each other's files. Record findings, decisions, and rerun checks. If independent review or another required gate is unavailable, record it as incomplete and keep the checker failure.

### 22–26 minutes: release decision and defense

Make a classroom release/recovery decision. Identify the baseline as the recovery point, explain how to rebuild a trusted RAG index, and record remaining risks. Give a two-minute defense to a peer, then listen to theirs: task and scope, main decision, strongest code/RAG evidence, residual risk, and recovery. No deployment or push is required.

From the **lab collection root**, validate your working record:

```sh
python examples/module-12/release-evidence/evidence_check.py examples/module-12/release-evidence/task.json ../m12-work/evidence/capstone.json > student-results/m12-check.json
```

If you chose another working-folder name, substitute it in this command. The blank record exits `1`. Open the report, address its `issues` with real evidence, and rerun. A complete record exits `0` with `valid: true`; the checker does not run your tests or verify the truth of your recorded review. Keep its report alongside your code, evidence index, RAG outputs, independent review/adjudication, release/recovery decision, and paired defense.

### Compare references after your attempt

Use the **lab collection root** terminal for these reference checks:

```sh
python -m unittest discover -s examples/module-12/release-evidence/solution/tests -v
python examples/module-12/release-evidence/evidence_check.py examples/module-12/release-evidence/task.json examples/module-12/release-evidence/evidence/complete.json
python examples/module-12/release-evidence/evidence_check.py examples/module-12/release-evidence/task.json examples/module-12/release-evidence/evidence/unsafe.json
python -m unittest discover -s examples/module-12/release-evidence/tests -v
```

Expected: **5 reference-solution tests**, complete exit `0`, unsafe exit `1`, and **13 checker tests**. These reference checks are separate from the tests you ran in `m12-work`.

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
