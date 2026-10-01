"""Current production sketch. This implementation does not satisfy the contract."""

from collections import defaultdict
from decimal import Decimal


def current_projection(checkpoint, journal, cut):
    latest = {}
    records = list(checkpoint["candidates"])
    records += [event["record"] for event in sorted(journal, key=lambda e: e["received_at"])
                if event["offset"] <= max(cut.values())]
    for record in records:
        if record["status"] not in ("captured", "settled"):
            continue
        latest[(record["kind"], record["id"])] = record

    balances = defaultdict(lambda: {"captured": 0, "refunded": 0})
    for record in latest.values():
        amount = (int(Decimal(record["amount"]) * 100)
                  if record["schema"] == 1 else record["amount_minor"])
        group = record["merchant"], record["order"], record["currency"]
        field = "captured" if record["kind"] == "capture" else "refunded"
        balances[group][field] += amount
    return {group: {**value, "net": value["captured"] - value["refunded"]}
            for group, value in balances.items()}
