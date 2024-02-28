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

    @api.depends("qty_done", "reserved_uom_qty")
    def _compute_barcode_scan_state(self):
        for line in self:
            if line.qty_done >= line.reserved_uom_qty:
                line.barcode_scan_state = "done"
            else:
                line.barcode_scan_state = "pending"

    def _barcodes_process_line_to_unlink(self):
        self.qty_done = 0.0

    def action_barcode_detailed_operation_unlink(self):
        for sml in self:
            if sml.product_uom_qty:
                sml._barcodes_process_line_to_unlink()
            else:
                sml.unlink()
            # HACK: To force refresh wizard values
            wiz_barcode = self.env["wiz.stock.barcodes.read.picking"].browse(
                self.env.context.get("wiz_barcode_id", False)
            )
            if wiz_barcode.option_group_id.barcode_guided_mode == "guided":
                wiz_barcode.todo_line_id.line_ids = wiz_barcode.todo_line_id.line_ids
                if not any(wiz_barcode.todo_line_id.line_ids.mapped("qty_done")):
                    wiz_barcode.fill_todo_records()
                    wiz_barcode.determine_todo_action()
            else:
                wiz_barcode.fill_todo_records()
                wiz_barcode.todo_line_id.line_ids = wiz_barcode.todo_line_id.line_ids
