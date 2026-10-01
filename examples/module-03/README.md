# M03 — Authorized RAG trace

Start with [the M03 steps in the workbook guide](../../WORKBOOK_GUIDE.md#m03--authorized-rag-trace), then consult the [shared RAG README](../rag-reference/README.md) and [runbook](../rag-reference/RUNBOOK.md).

The runnable offline path covers ingestion, authorization before ranking, cited answers, abstention, redacted telemetry, and eight evaluation categories. Its source stays at `examples/rag-reference/rag.py` so later workbook modules can use the same fixture and evidence hashes.

The optional full workbook extension asks for vector/full-text hybrid retrieval, reranking, LLM generation, and retry/clarification orchestration. Those components are not implemented by this lexical, deterministic reference.

[Context-packet practice](context-packet/README.md) supplies a learner packet, comparison packets, a small pricing repository, and a checker. Use it to practice choosing context before the RAG trace. The [RAG MCP bridge](../module-08/rag-mcp-bridge/README.md) is additional practice connecting M03 to M08.
