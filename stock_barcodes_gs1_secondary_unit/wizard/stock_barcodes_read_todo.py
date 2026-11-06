# Copyright 2023 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class WizStockBarcodesReadTodo(models.TransientModel):
    _inherit = ["wiz.stock.barcodes.read.todo", "product.secondary.unit.mixin"]
    _name = "wiz.stock.barcodes.read.todo"
    _secondary_unit_fields = {
        "qty_field": "product_uom_qty",
        "uom_field": "uom_id",
    }

    # The mixin declares secondary_uom_qty as precompute=True, but here it
    # depends on product_uom_qty, a stored computed field that is not
    # precomputed on this model. Opt our field out of precompute so the field
    # setup is consistent; it is still computed normally on write.
    secondary_uom_qty = fields.Float(precompute=False)

    @api.model
    def fields_to_fill_from_pending_line(self):
        res = super().fields_to_fill_from_pending_line()
        res.append("secondary_uom_id")
        return res
