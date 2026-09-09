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
    qty_picked = fields.Float(
        "Quantity picked",
        digits="Product Unit of Measure",
        readonly=False,
        store=True,
        compute="_compute_qty_picked",
    )

    @api.depends("picked", "quantity")
    def _compute_qty_picked(self):
        for line in self:
            if line.picked or line.state == "done":
                line.qty_picked = line.quantity
            else:
                # Editable stored compute used as a smart default: keep the
                # quantity accumulated by scanning.
                line.qty_picked = line.qty_picked

    @api.depends("qty_picked", "quantity_product_uom")
    def _compute_barcode_scan_state(self):
        for line in self:
            if line.barcode_scan_state == "done_forced" and line.qty_picked:
                # A line forced by scanning keeps its state until its picked
                # quantity is cleared; do not downgrade it to plain "done".
                line.barcode_scan_state = "done_forced"
            elif line.qty_picked and line.qty_picked >= line.quantity_product_uom:
                line.barcode_scan_state = "done"
            else:
                # Nothing picked (or no demand at all) is never "done": this
                # avoids flagging empty 0/0 lines as done.
                line.barcode_scan_state = "pending"

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        if self.env.context.get("stock_barcodes_assign_serials"):
            lines._stock_barcodes_set_scanned_from_dialog()
        return lines

    def write(self, vals):
        res = super().write(vals)
        if self.env.context.get("stock_barcodes_assign_serials") and (
            "lot_id" in vals or "lot_name" in vals
        ):
            self._stock_barcodes_set_scanned_from_dialog()
        return res

    def _stock_barcodes_set_scanned_from_dialog(self):
        """Count as scanned the lines that get a lot/serial in the detailed
        operations dialog opened from the barcode screen (e.g. with the
        generate serials widget), and link the new ones to their pending
        card so its counters include them.
        """
        wiz = self.env["wiz.stock.barcodes.read.picking"].browse(
            self.env.context.get("stock_barcodes_wiz_id")
        )
        for line in self:
            if not line.lot_id and not line.lot_name:
                continue
            if line.move_id and not line.picking_id:
                # The generate serials widget creates the lines from raw
                # values bypassing the dialog subview defaults, so they come
                # without picking and would be invisible to every view based
                # on picking.move_line_ids
                line.picking_id = line.move_id.picking_id
            line.qty_picked = line.quantity
            todo_lines = wiz.todo_line_ids.filtered(
                lambda t, line=line: line.move_id in t.stock_move_ids
                and line not in t.line_ids
            )
            todo_lines.line_ids = [(4, line.id)]

    def _barcodes_process_line_to_unlink(self):
        self.qty_picked = 0.0

    def action_barcode_detailed_operation_unlink(self):
        for sml in self:
            stock_move = sml.move_id
            stock_move.barcode_backorder_action = "pending"
            sml.unlink()
            # HACK: To force refresh wizard values
            wiz_barcode = self.env["wiz.stock.barcodes.read.picking"].browse(
                self.env.context.get("wiz_barcode_id", False)
            )
            stock_move._action_assign()
            wiz_barcode.fill_todo_records()
            wiz_barcode.determine_todo_action()
