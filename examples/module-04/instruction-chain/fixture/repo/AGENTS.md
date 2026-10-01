# Synthetic service repository

## Scope

Applies to the entire synthetic repository unless closer guidance narrows a rule.

## Repository map

- `services/` contains service code and tests.
- `docs/` contains approved engineering decisions.

## Commands

- test_command: python -m unittest discover -s tests -v
- lint_command: python -m compileall services

## Constraints

- dependency_policy: no new production dependencies
- data_boundary: synthetic data only

## Done when

- validation_gate: focused tests pass and the diff contains no unrelated changes
