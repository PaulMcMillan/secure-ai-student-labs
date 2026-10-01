"""Copy only the M04 starter into a separate student working folder."""

from pathlib import Path
import argparse
import shutil
import subprocess


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "examples/module-04/agents-md-workshop"
STARTER_FILES = (
    ".gitignore", "README.md", "AGENTS.md", "demo.py",
    "src/order_total/__init__.py", "src/order_total/pricing.py",
    "tests/test_pricing.py",
)


def copy_starter(destination: Path) -> Path:
    destination = destination.expanduser().resolve()
    if destination == ROOT or ROOT in destination.parents:
        raise ValueError("Choose a destination outside secure-ai-student-labs.")
    if destination.exists():
        raise ValueError("That destination already exists. Choose a new folder.")
    for name in STARTER_FILES:
        source = SOURCE / name
        if not source.is_file() or source.is_symlink():
            raise ValueError(f"Missing or invalid starter file: {name}")
    destination.mkdir(parents=True)
    for name in STARTER_FILES:
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(SOURCE / name, target)
    return destination


def initialize_git(destination: Path) -> bool:
    if not shutil.which("git"):
        return False
    # Local command overrides avoid requiring a student identity or signing setup.
    subprocess.run(["git", "init", "--quiet", str(destination)], check=True)
    hooks = destination / ".git" / "lab-empty-hooks"
    hooks.mkdir()
    git = ["git", "-c", f"core.hooksPath={hooks}", "-C", str(destination)]
    subprocess.run([*git, "add", "--", *STARTER_FILES], check=True)
    subprocess.run([
        *git, "-c", "user.name=M04 Lab", "-c", "user.email=lab@example.invalid",
        "-c", "commit.gpgsign=false", "commit", "--quiet", "-m", "M04 starter",
    ], check=True)
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path, help="New folder outside this repository")
    args = parser.parse_args()
    try:
        destination = copy_starter(args.destination)
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    try:
        baseline = initialize_git(destination)
    except (OSError, subprocess.CalledProcessError) as exc:
        print(f"Copied the starter, but Git setup did not finish: {exc}")
        baseline = False
    print(f"Open this folder in your coding agent: {destination}")
    if baseline:
        print("Created a local Git baseline so you can review changes with git diff.")
    else:
        print("No Git baseline is available; use your editor to compare changes.")
    print("From that folder, run: python -m unittest discover -s tests -v")
    print("Then run: python demo.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
