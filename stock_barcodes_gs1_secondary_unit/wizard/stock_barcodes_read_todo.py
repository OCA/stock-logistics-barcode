# Copyright 2023 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class WizStockBarcodesReadTodo(models.TransientModel):
    _inherit = "wiz.stock.barcodes.read.todo"

    secondary_uom_qty = fields.Float(
        string="Secondary Qty",
        digits="Product Unit of Measure",
        compute="_compute_secondary_uom",
    )
    secondary_uom_id = fields.Many2one(
        comodel_name="product.secondary.unit",
        string="Second unit",
        compute="_compute_secondary_uom",
    )

    def _compute_secondary_uom(self):
        for line in self:
            if (
                self.wiz_barcode_id.option_group_id.source_pending_moves
                == "move_line_ids"
            ):
                moves = line.line_ids
                qty = sum(m.secondary_uom_qty for m in moves.mapped("move_id")) - sum(
                    m.secondary_uom_qty for m in moves if m.qty_done
                )
            else:
                moves = line.stock_move_ids
                qty = sum(m.secondary_uom_qty for m in moves) - sum(
                    m.secondary_uom_qty for m in moves.move_line_ids if m.qty_done
                )
            line.secondary_uom_qty = qty
            line.secondary_uom_id = moves.secondary_uom_id[:1]

    @api.model
    def fields_to_fill_from_pending_line(self):
        res = super().fields_to_fill_from_pending_line()
        res.extend(["secondary_uom_qty", "secondary_uom_id"])
        return res
