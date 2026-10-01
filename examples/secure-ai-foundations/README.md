# Secure AI Foundations Evidence Checker

This dependency-free fixture teaches the difference between a security claim and a reviewable evidence packet. It does not inspect a host, start a model, call a network service, or change a file outside a test-created temporary directory.

From the repository root:

```powershell
python examples/secure-ai-foundations/secure_ai_check.py examples/secure-ai-foundations/profiles/declared-baseline.json
python examples/secure-ai-foundations/secure_ai_check.py examples/secure-ai-foundations/profiles/hardened-synthetic.json
python -m unittest discover -s examples/secure-ai-foundations/tests -v
```

Expected results:

- the declared-only baseline exits `1` because assertions are not sufficient evidence;
- the hardened synthetic packet exits `0`, covers seven AI modality families and eight platform evidence classes, and reports no host, model, network, or external action; and
- all seven tests pass.

The hardened packet is fictional course data. Its timestamps, evidence identifiers, devices, owners, and results are examples of the structure a production team must replace with its own approved evidence.
