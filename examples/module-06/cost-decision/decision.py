"""Recommend a role baseline and escalation gate from bounded factors."""
import argparse, json
from pathlib import Path

FACTORS = ("complexity", "ambiguity", "risk", "context", "output", "retry", "review")

def evaluate(data):
    issues=[]
    for key in (*FACTORS, "latency_priority"):
        value=data.get(key)
        if not isinstance(value, int) or not 1 <= value <= 5: issues.append(f"{key} must be an integer from 1 to 5")
    if issues: return {"valid":False,"issues":issues}
    score=sum(data[k] for k in FACTORS)
    if score >= 27 or data["risk"] >= 5: role="quality"
    elif score >= 17: role="balanced"
    else: role="fast"
    if data["latency_priority"] >= 4 and role == "quality" and data["risk"] < 5: role="balanced"
    gate = "escalate after one measured failure" if data["risk"] >= 4 else "escalate after two representative failures"
    return {"valid":True,"role":role,"factor_score":score,"escalation_gate":gate,"price_used":False}

def main():
    p=argparse.ArgumentParser(); p.add_argument("scenario",type=Path); a=p.parse_args()
    report=evaluate(json.loads(a.scenario.read_text(encoding="utf-8"))); print(json.dumps(report,indent=2,sort_keys=True)); return 0 if report["valid"] else 1
if __name__ == "__main__": raise SystemExit(main())
