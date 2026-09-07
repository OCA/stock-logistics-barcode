This module has no configuration of its own - it activates automatically once a
`product.secondary.unit` is given a `barcode` (Inventory > Configuration > Secondary Units, or
from the product form's secondary units list). Everything below happens through the normal
GS1 scanning wizards from `stock_barcodes_gs1`.

## Scanning a secondary unit's own barcode (AI 01)

Set the secondary unit's `barcode` to the same code printed on the package (e.g. a box label
GTIN). Scanning that code on the barcode-read wizard for a move:

- Matches the `product.secondary.unit` directly and sets it as the wizard's secondary unit.
- Sets the wizard's product to that secondary unit's product.
- If nothing else is entered manually, defaults the secondary quantity to 1 and derives the
  primary quantity from it (`secondary_uom_qty * factor`).

## Scanning a shipping/logistic label with an embedded count (AI 02 + AI 30/37)

A logistic label wraps several units of a product and states the GTIN of what's inside (AI 02)
together with a count (AI 30 or AI 37). Example, from a real test case: a secondary unit "box
AI02" (factor 8, i.e. 8 units per box) with `barcode` `18412598033091`, scanning
`0218412598033091<FNC1>373` (AI 02 with that GTIN, then AI 37 = 3):

- The AI 02 GTIN match sets the secondary unit on the wizard, the same way AI 01 does, and
  additionally records that the next quantity AI must land on the secondary unit.
- The AI 37 value (`3`) is then written to the wizard's secondary quantity, not its product
  quantity - the wizard ends up with `secondary_uom_qty = 3.0` and, since the secondary
  unit's factor is 8, `product_qty = 24.0` (3 boxes x 8 units).
- Scanning `...303` (AI 30, same GTIN) instead of `...373` produces the identical result -
  AI 30 and AI 37 are handled the same way.
- If the AI 02 GTIN does not match any secondary unit, the barcode falls through to the base
  module's own handling (a plain product/packaging match), and a later AI 30/37 sets the
  primary quantity as usual.

## Filling a whole transfer by scanning (batch picking-read wizard)

When using the wizard that fills an entire transfer's operations from successive scans (not
just one move at a time):

- The wizard's demand/done totals for a product (shown while scanning) add up the secondary
  quantity across all of that product's moves/lines in the transfer, not just the primary one.
- A scan that matches an *existing* move line for the same product but a *different* secondary
  unit creates/uses a separate line instead of merging into the wrong one.
- Scanning the same secondary unit again for a line that already has some secondary quantity
  recorded *adds* the newly scanned quantity to what was already there, instead of replacing
  it - successive scans of the same box accumulate.
- Once a move (or a move line that is the only one left for its move) already matches its
  primary demand exactly, the wizard auto-fills its secondary quantity from the move's own
  secondary demand - so an operator who finishes a line by weight alone still gets the
  expected piece count pre-filled, without having to scan or type it separately.

## Working through the pending-to-scan list

The "still to scan" list groups its rows by secondary unit as well as by product (unless the
"group key for pending records" option is turned off for that scanning session) - so if a
product is expected in two different secondary units on the same transfer, each shows as its
own row to complete. Filling a new scanned row from one of these pending rows carries the
secondary unit over automatically.

## Removing a scanned line

Deleting an already-scanned operation line from the wizard also resets its secondary quantity
to zero, so a reused line never keeps a stale count from what was previously scanned there.
