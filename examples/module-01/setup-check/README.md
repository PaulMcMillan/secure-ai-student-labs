# Codex Setup-Check Example

This dependency-free example is used in Day 1 M01, the Codex setup module. It gathers sanitized local setup evidence and validates model-routing examples plus both legacy sandbox and permission-profile teaching files without loading them into Codex.

## Safety properties

- No network access.
- No installation or configuration changes.
- No reading or printing of credential files or secret environment values.
- Authentication output is reduced to a category.
- MFA is recorded as external policy evidence rather than guessed; credential-store configuration is not opened.
- WIF environment presence and token-file existence may be reported, but the token and federation rule value are never read or printed.
- Repository paths are reduced to directory names and booleans.

## Run

From the student repository root:

```powershell
python examples/module-01/setup-check/setup_check.py
python examples/module-01/setup-check/config_guard.py examples/module-01/setup-check/configs/safe-project.toml
python examples/module-01/setup-check/config_guard.py examples/module-01/setup-check/configs/safe-permission-profile.toml
python -m unittest discover -s examples/module-01/setup-check/tests -v
```

The intentionally unsafe teaching config should exit nonzero:

```powershell
python examples/module-01/setup-check/config_guard.py examples/module-01/setup-check/configs/unsafe-project.toml
python examples/module-01/setup-check/config_guard.py examples/module-01/setup-check/configs/unsafe-mixed-permissions.toml
python examples/module-01/setup-check/config_guard.py examples/module-01/setup-check/configs/unsafe-astra-none.toml
```

Do not copy any example into `.codex/config.toml` during the lab. Model names, reasoning controls, and permission-profile syntax are update-sensitive. The exercise is evidence and analysis, not mutation of live Codex configuration. Verify model availability and aliases on the delivery day rather than assuming that this fixture describes the live account.
