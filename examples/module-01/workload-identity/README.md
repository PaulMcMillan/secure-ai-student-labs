# Workload Identity and Isolation Fixture

This dependency-free fixture validates a synthetic enterprise AI workload identity contract. It does not issue certificates, contact an identity provider, inspect the host, read a vault, connect to a network, or execute an agent.

Use it from the repository root:

```powershell
python examples/module-01/workload-identity/identity_check.py examples/module-01/workload-identity/identity-contract.json examples/module-01/workload-identity/profiles/unsafe.json
python examples/module-01/workload-identity/identity_check.py examples/module-01/workload-identity/identity-contract.json examples/module-01/workload-identity/profiles/hardened.json
python -m unittest discover -s examples/module-01/workload-identity/tests -v
```

The unsafe profile must exit `1`. The hardened profile must exit `0` and report that all control families pass. The checker also rejects malformed evidence types: booleans cannot stand in for integer lifetimes, and identities, actions, vault references, environments, egress destinations, and approval classes must use nonempty strings in the declared object/list shape.

The example uses a fictional SPIFFE-style workload identifier to illustrate short-lived workload-specific credentials and mutual peer verification. It does not require SPIFFE/SPIRE and does not claim that a certificate, token, network tag, or attestation alone proves authorization. Organizations may implement the same contract with approved cloud workload identity, mTLS PKI, hardware-backed platform attestation, signed audience-bound tokens, service-mesh policy, or another high-assurance mechanism.

<!-- UPDATE-SENSITIVE -->

For the 2026-09 Codex mapping, the upstream credential can be an OIDC token or SPIFFE JWT-SVID in a protected runtime-managed file, exchanged under an approved federation rule by Codex 0.148+ for short-lived Codex access. Native Windows requires elevated sandbox protection of that file. WIF still does not authenticate or authorize the downstream MCP server, database, repository, or production action; apply the fixture’s mutual identity, attestation, exact authorization, isolation, and approval controls independently.
