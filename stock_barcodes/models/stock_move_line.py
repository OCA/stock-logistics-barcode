# Copyright 2019 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    barcode_scan_state = fields.Selection(
        [("pending", "Pending"), ("done", "Done"), ("done_forced", "Done forced")],
        string="Scan State",
        default="pending",
        compute="_compute_barcode_scan_state",
        readonly=False,
        store=True,
    )

    @api.depends("qty_done", "product_uom_qty")
    def _compute_barcode_scan_state(self):
        for line in self:
            if line.qty_done >= line.product_uom_qty:
                line.barcode_scan_state = "done"
            else:
                line.barcode_scan_state = "pending"

    def action_barcode_detailed_operation_unlink(self):
        for sml in self:
            if sml.product_uom_qty:
                sml.qty_done = 0.0
            else:
                sml.unlink()
            wiz_barcode = self.env["wiz.stock.barcodes.read.picking"].browse(
                self.env.context.get("wiz_barcode_id", False)
            )
            if wiz_barcode.option_group_id.show_pending_moves:
                wiz_barcode.fill_todo_records()
