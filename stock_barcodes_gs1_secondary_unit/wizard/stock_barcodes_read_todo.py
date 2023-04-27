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
            moves = line.stock_move_ids or line.line_ids.mapped("move_id")
            line.secondary_uom_qty = sum(m.secondary_uom_qty for m in moves)
            line.secondary_uom_id = moves.secondary_uom_id[:1]

    @api.model
    def fields_to_fill_from_pending_line(self):
        res = super().fields_to_fill_from_pending_line()
        res.extend(["secondary_uom_qty", "secondary_uom_id"])
        return res
