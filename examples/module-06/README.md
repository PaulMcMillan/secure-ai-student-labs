# M06 — Model choice and reasoning effort

**Time: 20 minutes in pairs; allow 30 minutes working alone.** Compare **GPT-5.5**
and **GPT-6 Astra**, each at its lowest and highest available reasoning effort.
Investigate a payment projection rebuilt from a checkpoint while events were
still arriving. Check the balances, diagnosis, and proposed regression tests.

## Set up your Codex project

Complete setup before the activity.

1. In Codex, create a project named **M06 — Model choice**.
2. Select **secure-ai-student-labs/examples/module-06/starter-repo** in your
   existing student checkout as its only folder and working root.
3. Check that `CASE.md`, `CONTRACT.md`, the evidence files, and
   `current_projection.py` are directly in that folder.

The exercise stays in this subdirectory of the student repository. Read this
guide separately. Save answers in `student-results/m06/` at the student checkout
root, outside the Codex project's exercise folder. Keep the supplied files unchanged.
If repeating the activity, move previous answers out of the exercise folder first.

The case includes 21 saved candidates, 74 journal deliveries, two partition cuts,
and nine order groups. Apply the rules together:
versions can move a capture between orders, cancel a refund, resolve a conflict,
or change whether an earlier refund is eligible.

## 1. Run the investigation · 9 minutes

Split the models with a partner. Each person runs their model twice and then
shares both answers. Use these four configurations:

| Run | Model | Reasoning effort |
| --- | --- | --- |
| A | GPT-5.5 | Lowest available |
| B | GPT-5.5 | Highest available |
| C | GPT-6 Astra | Lowest available |
| D | GPT-6 Astra | Highest available |

Record the exact effort labels. Keep the other settings and tool access the same.
Effort labels differ between models; Ultra can use subagents, so note that in
your comparison. If a model is unavailable, pair with someone who has access.

For each run:

1. Start a fresh chat in **M06 — Model choice** and select the model and effort.
2. Paste the prompt below unchanged. Keep other answers and review material out
   of the chat.
3. Time the response. Allow up to **four minutes**. If it has not finished, stop
   it and record it as incomplete.
4. Save the final JSON as `A.json`, `B.json`, `C.json`, or `D.json` in your results
   folder. Wait until all runs finish before giving follow-up instructions.

### Prompt to paste

```text
Read CASE.md and complete the investigation using the evidence in this project. Return the requested JSON with both views, your diagnosis, and regression checks. You may use local calculations. Leave the supplied files unchanged and use only this project's files. Do not browse the web or read parent directories.
```

## 2. Check the answers · 8 minutes

For each completed answer, check both parts:

- **Results:** Does it report the right balances, blocked groups, conflicts, and
  deferred refunds at both cuts?
- **Explanation and tests:** Does its diagnosis match the code? Would its proposed
  regression tests accept correct behavior? Check each expected outcome against
  the selected versions and the contract.

Run the results checker from the **student checkout root**. It uses Python's
standard library. Substitute each answer filename in turn:

```sh
python examples/module-06/check_answer.py student-results/m06/A.json
```

The checker reports **22 balance and exception checks**. It does not grade the
explanation or test proposals. A complete, usable answer must pass those checks
and give an accurate diagnosis and accurate regression expectations. Record any
contradiction between the answer's numbers and its proposed tests.

| Run | Effort label | Response time | Checks / 22 | Diagnosis and tests correct? | Review time / corrections |
| --- | --- | --- | --- | --- | --- |
| A | | | | | |
| B | | | | | |
| C | | | | | |
| D | | | | | |

Record usage or cost if Codex shows it; otherwise write “not shown.” An incomplete
run is a time-budget result. Record correctness errors only in work you received.

After checking the answers yourself, compare them with the [review notes](review/README.md).

## 3. Choose a configuration · 3 minutes

Compare A with B, then C with D. Did higher effort improve the complete answer
enough to justify the time and usage? Then compare the two models. Count incorrect
test expectations and unsupported diagnoses as correction work, even when all
the balance checks pass. Higher effort can also make an answer worse; a tie is valid.

Write a short recommendation for similar investigations. Name the errors you
found, the review work each answer needed, and one other task you would try
before making this your default. These four runs do not establish a general
model ranking. Keep your answers, table, and recommendation.

## Follow-on review

**Time: 8 minutes.**

Use **GPT-6 Astra** to review the answer from **GPT-5.5 at low effort**. The aim
is to see whether it catches a real mistake and supports its correction with
evidence.

1. Keep your original answer unchanged. Copy it into the exercise folder as
   **earlier-answer.json**. If your answer was incomplete or you found no error,
   use the [saved GPT-5.5 low answer](review/sample-gpt55-low-answer.json) instead.
   This is an unedited response from a live run on the same case.
2. Start a fresh chat in **M06 — Model choice**. Select **GPT-6 Astra** with
   **High** reasoning effort. Give it the prompt below, without the results
   checker output or review guide.
3. Allow up to **four minutes** for the review, then check the reviewer's claims
   yourself against the contract, records, and code.

### Review prompt to paste

```text
Read CASE.md to understand the original assignment. Review earlier-answer.json against the contract, code, and evidence in this project. Check its balances, diagnosis, and proposed regression expectations. Identify substantive errors, cite the source records or code that establish each error, and give the corrected expectation. Say whether each correction changes the reported balances. If a claim is correct, preserve it; if you find no error, say so. Return a concise review of at most 500 words. Leave the supplied files unchanged, use only this project's files, and do not browse the web or read parent directories.
```

Keep a short record:

| Earlier claim | Reviewer's correction and evidence | Your verdict |
| --- | --- | --- |
| | | |

A useful review identifies a specific error and gives a correction supported by
the source. Check that it preserves correct results and does not invent a new
problem. For a proposed regression test, work through the relevant records and
confirm the expected outcome yourself.

Save the review and your verdict with your results. Move `earlier-answer.json`
out of the exercise folder afterward so it cannot influence a later comparison.

## Earlier workbook material

The Python files in [cost-decision](cost-decision/README.md) are optional accounting
practice from the earlier workbook.
