# INV-27 - Reject Invalid Reservation Quantities

`reserve` must raise `ValueError` when `requested` is zero or negative. Preserve successful subtraction for positive quantities and `ValueError` for insufficient stock. Add focused tests. Do not change dependencies, interfaces, or unrelated files.
