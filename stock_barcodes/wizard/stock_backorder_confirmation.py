# Copyright 2026 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class StockBackorderConfirmation(models.TransientModel):
    _inherit = "stock.backorder.confirmation"

    def _with_button_validate_picking_ids_context(self):
        """Force ``button_validate_picking_ids`` in the context from the
        wizard's own stored ``pick_ids``.

        ``process``/``process_cancel_backorder`` rely exclusively on that
        context key to know which pickings to validate, silently doing
        nothing (no error) if it points at pickings that no longer need
        it (e.g. already validated). In the barcode scanning wizard,
        validating a picking within a continued scanning session can reach
        this wizard's buttons with that key missing, or carrying a stale
        value left over from a previous validate in the same session.
        ``pick_ids`` is this wizard record's own stored data, correctly scoped
        to the pickings it was created for, so it is the source of truth when
        the context key is missing or stale.

        It must not replace a context key that already covers those pickings:
        the wizard only holds the pickings needing a backorder, while the
        validation can legitimately span more of them (validating a batch asks
        for a backorder on some of its pickings but must validate them all),
        and narrowing it down would leave the rest unvalidated.
        """
        picking_ids = self.env.context.get("button_validate_picking_ids")
        if self.pick_ids and not set(self.pick_ids.ids) <= set(picking_ids or []):
            return self.with_context(button_validate_picking_ids=self.pick_ids.ids)
        return self

    def process(self):
        return super(
            StockBackorderConfirmation, self._with_button_validate_picking_ids_context()
        ).process()

    def process_cancel_backorder(self):
        return super(
            StockBackorderConfirmation, self._with_button_validate_picking_ids_context()
        ).process_cancel_backorder()
