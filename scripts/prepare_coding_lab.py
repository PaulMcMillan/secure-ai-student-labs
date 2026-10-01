"""Prepare an independent M07 or M12 starter without copying worked answers."""

import argparse
from pathlib import Path
import shutil
import subprocess


ROOT = Path(__file__).resolve().parents[1]
LABS = {
    "m07": ("examples/module-07/change-workflow", {
        "starter-repo/AGENTS.md": "AGENTS.md",
        "starter-repo/README.md": "README.md",
        "starter-repo/WORK_ITEM.md": "WORK_ITEM.md",
        "starter-repo/src/__init__.py": "src/__init__.py",
        "starter-repo/src/inventory.py": "src/inventory.py",
        "starter-repo/tests/test_inventory.py": "tests/test_inventory.py",
    }),
    "m12": ("examples/module-12/release-evidence", {
        "starter/AGENTS.md": "AGENTS.md",
        "starter/WORK_ITEM.md": "WORK_ITEM.md",
        "starter/pricing.py": "pricing.py",
        "starter/tests/test_pricing.py": "tests/test_pricing.py",
        "task.json": "task.json",
        "evidence/starter.json": "evidence/capstone.json",
    }),
}


def prepare(module: str, destination: Path) -> bool:
    destination = destination.expanduser().resolve()
    if destination == ROOT or ROOT in destination.parents:
        raise ValueError("Choose a destination outside secure-ai-student-labs.")
    if destination.exists():
        raise ValueError("That destination already exists. Choose a new folder.")
    folder, files = LABS[module]
    for relative in files:
        source = ROOT / folder / relative
        if not source.is_file() or source.is_symlink():
            raise ValueError(f"Missing or invalid starter file: {relative}")
    destination.mkdir(parents=True)
    for relative, name in files.items():
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / folder / relative, target)
    (destination / ".gitignore").write_text("__pycache__/\n*.py[cod]\n", encoding="utf-8")
    (destination / ".gitattributes").write_text("* text=auto eol=lf\n", encoding="utf-8")
    if not shutil.which("git"):
        return False
    # Command-local settings need no personal identity or signing configuration.
    subprocess.run(["git", "init", "--quiet", str(destination)], check=True)
    hooks = destination / ".git" / "lab-empty-hooks"
    hooks.mkdir()
    git = ["git", "-c", f"core.hooksPath={hooks}", "-C", str(destination)]
    subprocess.run([*git, "add", "--", *files.values(), ".gitignore", ".gitattributes"], check=True)
    subprocess.run([
        *git, "-c", "user.name=Student Lab", "-c", "user.email=lab@example.invalid",
        "-c", "commit.gpgsign=false", "commit", "--quiet", "-m", f"{module.upper()} starter",
    ], check=True)
    subprocess.run([*git, "switch", "--quiet", "-c", f"student/{module}-exercise"], check=True)
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("module", choices=LABS)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    try:
        baseline = prepare(args.module, args.destination)
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        parser.exit(1, f"Setup did not finish: {exc}\nKeep any copied files; use a new destination to retry.\n")
    print(f"Open this folder in your coding agent: {args.destination.expanduser().resolve()}")
    print("From that folder, run: python -m unittest discover -s tests -v")
    if baseline:
        print(f"Created a Git baseline and student/{args.module}-exercise branch.")
        print("Record the baseline with: git rev-parse HEAD")
    else:
        print("Git is unavailable. Compare against the untouched starter in your editor.")
        if args.module == "m12":
            print("M12's final evidence gate needs a real Git baseline; pair with someone who has Git.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
