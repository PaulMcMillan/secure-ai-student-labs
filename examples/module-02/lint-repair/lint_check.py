"""Teaching-only unused plain-import check; never imports or rewrites its input.

This is deliberately a small, offline rule demonstrator, not a replacement for
a production linter. It supports top-level plain imports and counts Name loads
anywhere in the AST. It does not resolve scopes, aliases exported to other
modules, dynamic usage, import side effects, or from-imports.
"""

from __future__ import annotations

import argparse
import ast
from pathlib import Path


def lint(source: str) -> list[str]:
    tree = ast.parse(source)
    used = {node.id for node in ast.walk(tree)
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load)}
    issues = []
    for node in tree.body:
        if isinstance(node, ast.Import):
            for item in node.names:
                binding = item.asname or item.name.split(".", 1)[0]
                if binding not in used:
                    issues.append(f"{node.lineno}: L001 unused import '{item.name}'")
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    args = parser.parse_args()
    try:
        issues = lint(args.source.read_text(encoding="utf-8-sig"))
    except (OSError, SyntaxError, UnicodeError) as error:
        print(f"CHECK_ERROR: {type(error).__name__}")
        return 2
    for issue in issues:
        print(issue)
    print(f"Lint: {'FAIL' if issues else 'PASS'} ({len(issues)} issues)")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
