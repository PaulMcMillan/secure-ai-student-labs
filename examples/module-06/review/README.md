# M06 review notes

Use these notes after checking the answers yourself. Keep this page and the
checker output outside the model's context.

## Check the investigation

The [expected view data](expected_views.json) gives the exact numerical
results. Use the contract to check explanations. These interactions are useful
places to start:

- **Cancellation changes eligibility.** At `close`, north refund R4 is version 2,
  `canceled` (p-58). R3 is 1,800 (q-97), and capture C3 is 3,000 (q-98). R3 applies.
  R4 contributes nothing and is not deferred. R5 requires capture version 3;
  the selected capture is version 2, so R5 is deferred and is excluded from the
  refund-sum check. A test expecting R3 and R4 to be deferred at `close` is wrong.
- **The earlier cut is different.** At `preview`, R3 and R4 total 4,500 against
  C3's 4,000. Both must be deferred. Do not carry that decision into `close`.
- **Conflicts affect more than one group.** North C4 conflicts at `preview` across
  orders A and B, blocking both. Its unambiguous version 3 resolves that conflict
  at `close`. South C7 still conflicts across B and C. West refund R2 conflicts
  at `close`; it belongs in `conflicts`, not also in `deferred_refunds`.
- **Identity has three parts.** The current code already separates capture IDs
  from refund IDs with `(kind, id)`. Its missing key field is `merchant`. A claim
  that this key merges a capture with a refund of the same ID misreads the code.
- **Eligibility can change without a new refund.** East R4 becomes eligible when
  C2 moves to EUR order E1. East R3 then refers to the wrong group. Recheck all
  selected refunds against each view's final capture state.

Other defects include filtering by a global maximum offset, admitting deliveries
already covered by the checkpoint, choosing by arrival instead of version,
filtering statuses before choosing versions, scaling JPY as though it had two
minor-unit decimal places, omitting zero groups, and failing to check conflicts
and refund dependencies. Equivalent diagnoses and test cases are welcome.

The evidence describes a display projection. It does not prove what a bank
charged or that a payout was sent.

## Check the follow-on review

The [saved GPT-5.5 low answer](sample-gpt55-low-answer.json) is an unedited live
response to this case. Use it if your own answer was incomplete or had no errors.
Copy only that answer into the exercise folder as `earlier-answer.json`.

The sample passes all 22 balance and exception checks. Its final regression
proposal wrongly says north refunds R3 and R4 should both be deferred at `close`.
R4 was canceled by p-58, so only R3's 1,800 participates in the sum check against
C3's 3,000. R3 applies; R4 is neither applied nor deferred. The sample's balance
table already reflects that correct outcome.

The sample also claims that `(kind, id)` mixes capture and refund IDs. This key
already separates kinds; its missing field is `merchant`.

Check whether the reviewing model identifies these errors, cites the evidence,
and preserves the correct balances. Accept equivalent wording and other
corrections that you can verify against the source.
