# M01 — Hands-on setup

This is the small practice task for the revised **M01 S006** slide. It needs Python 3.11+ and the course-approved coding agent. Copy this folder to your own writable practice location and open that copy in the agent. It contains only this README, `practice.txt`, and `check_setup.py`.

1. Confirm which account/connection the agent uses, which checkout it sees, and where commands run. Select the permissions agreed with your instructor. Use the normal sign-in flow for credentials.
2. Ask the agent to read `check_setup.py` and explain the result it expects. Run `python check_setup.py` from this folder. The starter prints “Practice edit pending” and exits `1`.
3. Ask: “Change only practice.txt from status: pending to status: ready. Run python check_setup.py in this same checkout and report the changed line and result.”
4. Inspect the one-line edit and check output. Expected: `PASS: this checkout contains the practice edit and Python ran the check.` and exit `0`. If commands run remotely, verify that the remote copy contains the edit.
5. Keep or revert your own practice edit as the instructor directs. To repeat the exercise, restore `status: pending` in your copy.

Do not change the checker to obtain a pass. This demonstrates file access, an edit, and a local check; it does not certify account permissions or sandbox enforcement. Use `python3` or `py -3` if that is your Python command.

If sign-in, access, or Python is unavailable, pair with a learner or work through the issue with the instructor. Mark any unrun step “not run.”

[Full setup directions](../../../WORKBOOK_GUIDE.md#m01--hands-on-setup)
