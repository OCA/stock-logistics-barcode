This module teaches the GS1 barcode reading wizards (`stock_barcodes_gs1`) to recognize a
product's **secondary unit** (from `stock_secondary_unit`/`product_secondary_unit` - e.g. a
count of pieces or boxes alongside a product that is actually measured by weight) directly
from a scanned label, and to route the scanned quantity to the right field.

A `product.secondary.unit` record (e.g. "box of 8 pieces") gets its own `barcode`. Two GS1
Application Identifiers are checked against it:

- **AI 01** (GTIN of the trade item itself): scanning the secondary unit's own barcode (e.g. a
  box label) identifies both the product and which secondary unit/pack size it represents in
  one scan.
- **AI 02** (GTIN of the contained trade item, used on a logistic/shipping label that wraps
  several units of a product): matching it against a secondary unit additionally arms the
  wizard so that a **count Application Identifier scanned right after it in the same barcode**
  - **AI 30** (Variable count of items) or **AI 37** (Count of items) - gets routed to the
  secondary unit's quantity instead of the product's primary quantity (e.g. weight). Both AIs
  share one hook in the base module (`_set_gs1_product_qty`), so both are covered the same way
  - counting 3 boxes of fish sold by weight must land on "3 pieces", never get treated as "3 kg".

Beyond the single-operation scanning wizard, the module also extends:

- The **batch picking-read wizard** (scan-driven filling of a whole transfer): keeps a running
  total of demanded vs. already-scanned secondary quantity per product, keeps scans of
  different secondary units of the same product on separate move lines instead of merging
  them, adds up the secondary quantity when a further scan matches an existing line, and
  auto-fills the secondary quantity once a move/line's own primary demand is already fully
  covered by what was scanned.
- The **pending-to-scan ("to-do") list**: groups pending lines by secondary unit too (so
  different secondary units of the same product show as separate rows to complete), and
  carries the secondary unit over when a new row is filled from a pending one.
- Removing an already-scanned line resets its secondary quantity back to zero, so it can't
  resurface stale if the line is reused.
