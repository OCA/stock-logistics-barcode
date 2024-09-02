# Copyright 2023 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class WizStockBarcodesReadTodo(models.TransientModel):
    _inherit = ["wiz.stock.barcodes.read.todo", "product.secondary.unit.mixin"]
    _name = "wiz.stock.barcodes.read.todo"
    _secondary_unit_fields = {
        "qty_field": "product_uom_qty",
        "uom_field": "uom_id",
    }

    @api.model
    def fields_to_fill_from_pending_line(self):
        res = super().fields_to_fill_from_pending_line()
        res.append("secondary_uom_id")
        return res
