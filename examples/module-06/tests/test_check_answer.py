import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('check_answer', ROOT / 'check_answer.py')
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class AnswerChecks(unittest.TestCase):
    def setUp(self):
        self.expected = json.loads(checker.EXPECTED.read_text())
        self.answer = copy.deepcopy(self.expected)

    def check(self):
        return checker.check_views(self.answer, self.expected)

    def test_reference_and_reordering(self):
        for view in self.answer['views'].values():
            for values in view.values():
                values.reverse()
        self.assertEqual(self.check(), (22, 22, []))

    def test_wrong_known_subtotal_and_block_status(self):
        row = self.answer['views']['close']['balances'][0]
        row['net'] = 0
        row['blocked'] = False
        passed, total, errors = self.check()
        self.assertEqual((passed, total), (21, 22))
        self.assertTrue(any('north/A/USD' in e and 'net:' in e and 'blocked:' in e for e in errors))

    def test_missing_zero_group(self):
        self.answer['views']['preview']['balances'].pop(3)
        self.assertTrue(any('south/B/USD: missing' in e for e in self.check()[2]))

    def test_duplicate_and_extra_groups(self):
        rows = self.answer['views']['close']['balances']
        rows.append(copy.deepcopy(rows[0]))
        extra = copy.deepcopy(rows[1]); extra['order'] = 'invented'
        rows.append(extra)
        errors = self.check()[2]
        self.assertTrue(any('more than once' in e for e in errors))
        self.assertTrue(any('unexpected group' in e for e in errors))

    def test_canceled_refund_is_not_deferred(self):
        self.answer['views']['close']['deferred_refunds'].append('north/refund/R4')
        self.assertTrue(any("extra ['north/refund/R4']" in e for e in self.check()[2]))

    def test_conflicting_refund_is_not_also_deferred(self):
        self.answer['views']['close']['deferred_refunds'].append('west/refund/R2')
        self.assertEqual(self.check()[0], 21)

    def test_bad_shape_is_reported(self):
        self.answer['views']['preview'] = None
        self.assertEqual(self.check()[0], 11)
        self.assertEqual(self.check()[1], 22)

    def test_json_code_fence_is_accepted(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'answer.md'
            path.write_text('```json\n' + json.dumps(self.answer) + '\n```\n')
            self.assertEqual(checker.read_answer(path), self.answer)


if __name__ == '__main__':
    unittest.main()
