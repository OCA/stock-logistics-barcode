# Copyright 2023 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class WizStockBarcodesReadTodo(models.TransientModel):
    _inherit = "wiz.stock.barcodes.read.todo"

    review_picking_batch = fields.Boolean(related="wiz_barcode_id.review_picking_batch")

    @api.depends(
        "line_ids",
        "line_ids.qty_picked",
        "line_ids.product_uom_qty",
        "line_ids.barcode_scan_state",
        "line_ids.barcodes_is_reviewed",
        "qty_done",
        "product_uom_qty",
    )
    def _compute_state(self):
        # The compute can batch records from several wizards, so split by
        # review mode instead of reading the flag on a multi-recordset
        review_records = self.filtered("wiz_barcode_id.review_picking_batch")
        for rec in review_records:
            if rec.line_ids.filtered(lambda ln: not ln.barcodes_is_reviewed):
                rec.state = "pending"
            else:
                rec.state = "done"
        return super(WizStockBarcodesReadTodo, self - review_records)._compute_state()

    def action_confirm_review(self):
        self.line_ids.barcodes_is_reviewed = True
