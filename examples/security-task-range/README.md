# Security Task Range

Dependency-free, offline simulator for the course-wide **Securing the Task/Activity** series. It evaluates inert JSON attack records against named control sets. It does not execute scenario actions.

Run this block from `examples/security-task-range`.

```powershell
python security_range.py self-test
python security_range.py list
python security_range.py run M03 --profile vulnerable
python security_range.py run M03 --profile hardened
python security_range.py run M03 --controls identity_filter_before_ranking,provenance_and_instruction_separation,citation_abstention_and_quarantine
python -m unittest discover -s tests -v
```

`vulnerable` intentionally supplies no chapter controls and should report `COMPROMISED`. `hardened` supplies every required control and should report `BLOCKED`. A custom control list lets learners test incomplete defenses. Every result includes redacted signals and response actions.

Safety properties are enforced by design: the program imports no network or process-execution libraries, accepts no URLs or credentials, reads only its bundled scenario catalog, and writes nothing.

## Workbook mapping

The scenario IDs retain the original storyline order. Scenario `M01` (boundary mapping) supports the current workbook M02; scenario `M02` (setup) supports current workbook M01. Other scenario IDs follow their corresponding modules.
