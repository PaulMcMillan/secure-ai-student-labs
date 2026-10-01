# Secure AI Agentic Platform Engineering — Student Labs

Runnable source for the **Day 1 M02 and M03** student workbook exercises.

## Download

**[Download the ZIP](https://github.com/PaulMcMillan/secure-ai-student-labs/archive/refs/heads/main.zip)** and extract it, or:

```sh
git clone https://github.com/PaulMcMillan/secure-ai-student-labs.git
cd secure-ai-student-labs
```

Use **Python 3.11 or newer**. No packages, API keys, or model calls are needed for these fixtures. Run the commands below from the extracted repository root. If your Python command is `python3` or `py -3`, use that in place of `python`.

```sh
python --version
python scripts/validate_course.py
```

Expected: **13 unit tests pass**, followed by successful RAG ingestion, a cited query, and **8 passing evaluation cases**. Validation creates its index in a temporary directory. The M03 commands below create the working index for your own queries.

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

## Workbook notes

- Use a disposable copy or your own branch for edits.
- M02 now lives under `examples/module-02/order-service`. If your workbook prints the older M01 directory for this exercise, use the M02 commands above. References to the “AITrainer root” mean this repository root in the student bundle.
- Historical `course/.../lab-guide.md` references identify the workbook's authoring sources. Follow the instructions printed in your workbook and the lab READMEs here.
- If a workbook paragraph puts several commands on one line, run each command separately.
- All corpus documents, identities, and policy records are synthetic classroom fixtures. Identity arguments simulate trusted claims; they are not a production authentication system.
- Use the separately supplied student workbook and slides alongside this source bundle. Other modules will be published separately.
