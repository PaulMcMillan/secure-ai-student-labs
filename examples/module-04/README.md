# M04 — Writing useful project instructions

The current M04 slides use the [order calculator starter](agents-md-workshop/README.md). It runs independently of the rest of this collection and needs only Python's standard library.

## Prepare your working copy

From the **secure-ai-student-labs root**, run:

```sh
python scripts/prepare_m04.py ../m04-work
```

This copies only the seven starter files into a new folder beside this repository. It refuses to overwrite an existing folder. If Git is installed, it creates a local baseline commit so you can review your changes. It does not push anything or change your Git identity settings.

Open **m04-work** as the project in your coding agent. From that folder, run:

```sh
python -m unittest discover -s tests -v
python demo.py
```

Expected baseline: **4 passing tests** and `Order total: 13.50`.

You can also copy the contents of `agents-md-workshop` into a new folder yourself. Use `python3` or `py -3` if that is how you run Python.

Complete preparation before the 15-minute activity begins.

## During class

Follow the [M04 workbook directions](../../WORKBOOK_GUIDE.md#m04--repository-guidance) or the single work slide, **M04 S014 — Practice: write, try, and revise**. Keep the workbook guide outside your `m04-work` project and give the agent only your guides and the stated task prompts. The starter contains no completed local guide, exercise walkthrough, or worked solution.

Keep your work in your own copy. You do not need an API key, extra Python packages, or access to AITrainer. A coding agent is used for the live activity; the slides also describe a written alternative.

## Earlier workbook lab

The [instruction-chain fixture](instruction-chain/README.md) remains available for the older workbook tracing activity. Its modeled selection rules are a separate exercise. Use the order calculator for the revised M04 session.
