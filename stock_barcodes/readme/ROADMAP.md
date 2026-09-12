- Execute action_done() method outside onchange environment.
- Allow create product when a barcode has not been found.
- Allow to select picking reading its barcode.
- Allow to select multiple pickings to process scanned products.

Technical debt (see `docs/TECHNICAL.md`):

- `action_confirm()` persists the onchange cache through
  `_convert_to_write(self._cache)`, relying on ORM internals.
- Rename the `onchange_*` helpers to `_onchange_*` (silent API break for
  downstream overrides, needs coordination).
- Drop the deprecated misspelled aliases (`_set_messagge_info`,
  `check_location_contidion`, `check_lot_contidion`) after one migration
  cycle.
