"""Check the M06 balance data. Review diagnosis and regression checks separately."""

import argparse
import json
from pathlib import Path
import sys

EXPECTED = Path(__file__).parent / 'review' / 'expected_views.json'
GROUP_FIELDS = ('merchant', 'order', 'currency')
VALUE_FIELDS = ('captured', 'refunded', 'net', 'blocked')


def read_answer(path):
    text = Path(path).read_text(encoding='utf-8').strip()
    if text.startswith('```') and text.endswith('```'):
        text = '\n'.join(text.splitlines()[1:-1])
    result = json.loads(text)
    if not isinstance(result, dict) or not isinstance(result.get('views'), dict):
        raise ValueError('Expected a JSON object containing views.')
    return result


def check_views(answer, expected):
    """Return passed core checks, total checks, and useful discrepancy messages."""
    passed = 0
    total = 0
    errors = []
    for name, target in expected['views'].items():
        actual = answer.get('views', {}).get(name, {})
        if not isinstance(actual, dict):
            actual = {}
        rows = actual.get('balances', [])
        if not isinstance(rows, list):
            rows = []
        indexed = {}
        duplicates = set()
        for row in rows:
            if not isinstance(row, dict) or not all(isinstance(row.get(f), str) for f in GROUP_FIELDS):
                errors.append(f'{name}: each balance row needs merchant, order, and currency.')
                continue
            key = tuple(row[f] for f in GROUP_FIELDS)
            if key in indexed:
                duplicates.add(key)
            indexed[key] = row
        expected_keys = {tuple(row[f] for f in GROUP_FIELDS) for row in target['balances']}
        for extra in sorted(set(indexed) - expected_keys):
            errors.append(f'{name}: unexpected group {"/".join(extra)}.')
        for row in target['balances']:
            total += 1
            key = tuple(row[f] for f in GROUP_FIELDS)
            found = indexed.get(key)
            label = f'{name} {"/".join(key)}'
            if key in duplicates:
                errors.append(f'{label}: group appears more than once.')
            elif found is None:
                errors.append(f'{label}: missing balance row.')
            else:
                differences = [f'{f}: got {found.get(f)!r}, expected {row[f]!r}'
                               for f in VALUE_FIELDS if found.get(f) != row[f]]
                if differences:
                    errors.append(f'{label}: ' + '; '.join(differences))
                else:
                    passed += 1
        for field in ('conflicts', 'deferred_refunds'):
            total += 1
            values = actual.get(field)
            if not isinstance(values, list) or not all(isinstance(v, str) for v in values):
                errors.append(f'{name} {field}: expected a list of identity strings.')
            elif set(values) == set(target[field]):
                passed += 1
            else:
                missing = sorted(set(target[field]) - set(values))
                extra = sorted(set(values) - set(target[field]))
                errors.append(f'{name} {field}: missing {missing}; extra {extra}.')
    return passed, total, errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('answer', type=Path, help='Saved model JSON response')
    args = parser.parse_args()
    try:
        answer = read_answer(args.answer)
        expected = json.loads(EXPECTED.read_text(encoding='utf-8'))
    except (OSError, ValueError) as exc:
        print(f'Could not read the answer: {exc}', file=sys.stderr)
        return 2
    passed, total, errors = check_views(answer, expected)
    print(f'Balance and exception checks: {passed}/{total}')
    for error in errors:
        print(f'FAIL: {error}')
    print('Also review the diagnosis and regression expectations. Correct numbers alone do not establish a correct investigation.')
    for field in ('diagnosis', 'regression_checks'):
        if not answer.get(field):
            print(f'MISSING: {field}')
            errors.append(f'Missing {field}')
    return 1 if errors else 0


if __name__ == '__main__':
    raise SystemExit(main())
