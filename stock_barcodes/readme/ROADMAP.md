- Execute action_done() method outside onchange environment.
- Allow create product when a barcode has not been found.
- Allow to select picking reading its barcode.
- Allow to select multiple pickings to process scanned products.

- Barcode nomenclatures: read the quantity or weight embedded in a
  barcode (e.g. EAN-13 variable weight/price prefixes), common for fresh
  food. GS1-128 is handled by `stock_barcodes_gs1`.
- Products with several barcodes: only the product `barcode` field and
  the packaging barcodes are matched.
- Scrap from the scan screen (damaged goods found while picking or
  counting).
- Manufacturing orders: consume components and produce finished
  products by scanning.
- Print product, lot or package labels from the scan screen, e.g. right
  after receiving.
- Inventory: choose the option group and the default location per
  warehouse. The inventory screen always uses the *Inventory* group and
  opens on the first warehouse stock location.
- Search picking from product: order the candidate pickings by priority
  and scheduled date instead of by stock move creation.
Option overlaps to review:

- Some behavior depends on the group code (*IN*, *OUT*, *REL*) instead of
  explicit options.
- *Auto put in pack* also applies when the picking is validated outside
  the barcode interface.

Technical debt (see `docs/TECHNICAL.md`):

- `action_confirm()` persists the onchange cache through
  `_convert_to_write(self._cache)`, relying on ORM internals.
- Rename the `onchange_*` helpers to `_onchange_*` (silent API break for
  downstream overrides, needs coordination).
- Drop the deprecated misspelled aliases (`_set_messagge_info`,
  `check_location_contidion`, `check_lot_contidion`) after one migration
  cycle.
- Remove unused code: `stock.barcodes.option.message`,
  `_scanned_location()`, the `skip_backorder` branch of
  `stock.picking.button_validate()` and the unreachable
  `visible_force_done` assignment for *Allow negative quant* in
  `check_done_conditions()`.
