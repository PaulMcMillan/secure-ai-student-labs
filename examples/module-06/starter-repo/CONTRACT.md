# Projection contract

## 1. Select the evidence for a view

The checkpoint already includes every delivery through its saved offset in each
partition. Start with **all** its saved candidates, including pending records,
canceled records, unresolved refunds, and both sides of any conflict.

Add journal deliveries only when:

```text
checkpoint.offsets[partition] < delivery.offset <= view.cut[partition]
```

Apply this filter before choosing versions. Offsets are local to a partition.
File order, delivery ID, and `received_at` do not decide which state wins.
The two views have different cuts; reconstruct each from the same checkpoint.

## 2. Normalize records and choose current state

The object identity is `(merchant, kind, id)`. IDs may repeat across merchants
and between `capture` and `refund`. Every record is a **complete replacement
snapshot** of that object, never an amount to add to its previous version.

- Schema 1 has `amount`, a decimal string in major units. Convert it exactly to
  integer minor units: USD/EUR have two decimal places; JPY has none.
- Schema 2 has integer `amount_minor` already in minor units.
- All supplied records are valid under their schema. Versions are positive integers.
- Normalize first. Schema number and transport fields are not part of the
  normalized body. The body is `merchant`, `kind`, `id`, `version`, `order`,
  `currency`, minor-unit amount, `status`, and, for refunds, `capture_id` and
  `requires_capture_version`.

For each identity, select the highest version in the view. Repeated deliveries
with the same normalized body are one candidate. If that highest version has
two different normalized bodies, the identity is **conflicting**. A higher
version resolves a lower-version conflict. Lower conflicting versions do not
poison a newer unambiguous version.

Exclude a conflicting object from amounts. Block every order group named by
its highest-version candidates, even when one candidate is pending or canceled.
Never fall back to a lower version, select whichever arrived last, or add the
conflicting amounts together.

## 3. Apply captures and refunds

A selected capture contributes its amount only when `status` is `captured`.
`pending` and `voided` contribute zero. A later version may change the amount,
status, order, or currency. Remove the old contribution when that happens.

A selected refund contributes only when `status` is `settled`. `pending` and
`canceled` contribute zero and are not deferred. Choose the version **before**
filtering by status.

A settled refund is eligible only if its referenced capture:

1. Has the same merchant and `capture_id` and is unambiguous.
2. Is currently `captured`, in the same order and currency as the refund.
3. Has a selected version at least `requires_capture_version`.

Otherwise, list the refund as deferred and block its own order group. Revisit
checkpoint refunds against the final capture state of each view; a refund that
was ineligible at the checkpoint may now be eligible, and the reverse can happen.

For each capture, sum **all otherwise eligible settled refunds** across distinct
refund identities. If that sum exceeds the capture amount, defer **all** those
refunds and block their group. Do not clip the sum or select an arbitrary subset.
An ineligible refund does not participate in this sum. Equality is allowed.

## 4. Report balances and release status

For each requested `(merchant, order, currency)` group:

```text
captured = sum of contributing captures
refunded = sum of eligible refunds that survived the per-capture sum check
net = captured - refunded
```

Set `blocked` if the group has a conflict or a deferred settled refund. A group
with only ordinary pending or canceled objects is not blocked. A blocked group's
reported amounts are known subtotals, not a claim that the remaining uncertainty
is worth zero. Groups with no contributing objects still appear as zero rows.

This contract governs the display projection. It does not establish what a bank
actually charged, why a duplicate was delivered, or whether a payout was sent.
