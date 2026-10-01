# Reconcile a payment projection after a replay

A display service was rebuilt from a checkpoint while live events continued to
arrive. Its totals disagree with the payment ledger. Operations wants to know
which order balances can be released at two recorded cuts of the stream.

This is synthetic evidence. All rules needed for the task are in this folder.

## Evidence

- `CONTRACT.md`: the authoritative projection rules.
- `checkpoint.json`: saved candidates and the last included offset in each partition.
- `journal.jsonl`: deliveries around the checkpoint and both review cuts.
- `cuts.json`: the partition offsets for `preview` and `close`, plus the order groups to report.
- `current_projection.py`: the current, defective implementation.

Read the contract and the evidence. Reconstruct both views independently from
the checkpoint. You may use local calculations or temporary scripts. Leave the
supplied files unchanged. Use only files in this folder; the exercise guide and
review material in parent directories are outside the task.

## Deliverable

Return one JSON object with `views`, `diagnosis`, and `regression_checks`.

`views` must contain `preview` and `close`. Each view has:

- `balances`: one row for every group in `cuts.json`, including zero balances.
  Each row has `merchant`, `order`, `currency`, integer `captured`, `refunded`,
  and `net` in minor units, and boolean `blocked`.
- `conflicts`: the conflicting identities, as `merchant/kind/id` strings.
- `deferred_refunds`: the settled refunds that cannot be applied, using the
  same identity format. A conflicting refund belongs only in `conflicts`.

Array ordering does not matter. Use empty arrays when appropriate. Do not sum
different currencies. `captured`, `refunded`, and `net` are known subtotals even
when a group is blocked.

In `diagnosis`, explain at least four independent defects in the current code
and the narrow changes needed to meet the contract. In `regression_checks`,
give concrete inputs and expected outcomes for those defects. Keep these two
fields together under 600 words; there is no word limit on the balance data.
Do not implement a replacement service.
