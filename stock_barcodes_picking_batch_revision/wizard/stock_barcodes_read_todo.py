# Copyright 2023 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class WizStockBarcodesReadTodo(models.TransientModel):
    _inherit = "wiz.stock.barcodes.read.todo"

    review_picking_batch = fields.Boolean(related="wiz_barcode_id.review_picking_batch")

    @api.depends(
        "line_ids",
        "line_ids.qty_done",
        "line_ids.product_uom_qty",
        "line_ids.barcode_scan_state",
        "qty_done",
        "product_uom_qty",
    )
    def _compute_state(self):
        if not self.wiz_barcode_id.review_picking_batch:
            return super()._compute_state()
        for rec in self:
            if rec.line_ids.filtered(lambda ln: not ln.barcodes_is_reviewed):
                rec.state = "pending"
            else:
                rec.state = "done"

    def action_confirm_review(self):
        self.line_ids.barcodes_is_reviewed = True
