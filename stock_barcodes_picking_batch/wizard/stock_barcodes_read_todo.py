# Copyright 2026 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class WizStockBarcodesReadTodo(models.TransientModel):
    _inherit = "wiz.stock.barcodes.read.todo"

    picking_names = fields.Char(compute="_compute_picking_names")

    @api.depends("wiz_barcode_id.picking_mode", "stock_move_ids.picking_id")
    def _compute_picking_names(self):
        """Picking references of the grouped moves, only needed to tell them
        apart when reading a batch"""
        for todo in self:
            todo.picking_names = (
                ", ".join(todo.stock_move_ids.picking_id.mapped("name"))
                if todo.wiz_barcode_id.picking_mode == "picking_batch"
                else False
            )
