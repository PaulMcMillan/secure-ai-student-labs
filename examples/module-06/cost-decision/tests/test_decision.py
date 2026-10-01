import unittest
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
from decision import evaluate

class DecisionTests(unittest.TestCase):
    def base(self): return {"complexity":2,"ambiguity":2,"risk":2,"context":2,"output":2,"retry":2,"review":2,"latency_priority":2}
    def test_routine_is_fast(self): self.assertEqual(evaluate({**self.base(),"ambiguity":1,"risk":1})["role"],"fast")
    def test_midrange_is_balanced(self): self.assertEqual(evaluate({**self.base(),"complexity":4,"context":4})["role"],"balanced")
    def test_high_risk_is_quality(self): self.assertEqual(evaluate({**self.base(),"risk":5})["role"],"quality")
    def test_latency_can_lower_noncritical_quality(self): self.assertEqual(evaluate({k:4 for k in self.base()} | {"risk":4,"latency_priority":5})["role"],"balanced")
    def test_high_risk_escalates_after_one_failure(self): self.assertIn("one measured",evaluate({**self.base(),"risk":4})["escalation_gate"])
    def test_invalid_factor_is_rejected(self): self.assertFalse(evaluate({**self.base(),"risk":9})["valid"])
    def test_no_price_is_used(self): self.assertFalse(evaluate(self.base())["price_used"])
if __name__ == "__main__": unittest.main()
