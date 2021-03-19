# Copyright 2021 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    barcode = fields.Char("Barcode", copy=False, index=True)

    def write(self, vals):
        if "barcode" in vals and "barcode_write" not in self.env.context:
            barcode = vals.pop("barcode", None)
            self.sudo().with_context(barcode_write=True).write({"barcode": barcode})
        if not vals:
            # Avoid to call super if vals has not values due to access rules errors
            return True
        return super().write(vals)

    @api.model
    def create(self, vals):
        if "force_barcode" in self.env.context:
            vals["barcode"] = self.env.context["force_barcode"]
        return super().create(vals)
