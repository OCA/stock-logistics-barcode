# Copyright 2024 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    barcode_backorder_action = fields.Selection(
        [
            ("pending", "Pending"),
            ("create_backorder", "Create Backorder"),
            ("skip_backorder", "No Backorder"),
        ],
        string="Backorder action",
        default="pending",
    )
    qty_picked = fields.Float(
        "Quantity picked",
        digits="Product Unit of Measure",
        compute="_compute_qty_picked",
    )

    @api.depends("move_line_ids.qty_picked")
    def _compute_qty_picked(self):
        for move in self:
            move.qty_picked = sum(move.mapped("move_line_ids.qty_picked"))

    def _action_done(self, cancel_backorder=False):
        moves_cancel_backorder = self.browse()
        if not cancel_backorder:
            moves_cancel_backorder = self.filtered(
                lambda sm: sm.barcode_backorder_action == "skip_backorder"
            )
            super(StockMove, moves_cancel_backorder)._action_done(cancel_backorder=True)
        moves_backorder = self - moves_cancel_backorder
        moves_backorder.barcode_backorder_action = "pending"
        return super(StockMove, moves_backorder)._action_done(
            cancel_backorder=cancel_backorder
        )

    def copy_data(self, default=None):
        vals_list = super().copy_data(default=default)
        for vals in vals_list:
            vals.pop("barcode_backorder_action", None)
        return vals_list
