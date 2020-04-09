# Copyright 2019 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class WizStockBarcodesRead(models.AbstractModel):
    _inherit = "wiz.stock.barcodes.read"

    life_date = fields.Datetime(string="End of Life Date",)
    use_date = fields.Datetime(string="Best before Date",)

    def _prepare_lot_values(self, barcode_decoded):
        res = super()._prepare_lot_values(barcode_decoded)
        preferred_date = barcode_decoded.get("15", False)
        life_date = barcode_decoded.get("17", False)
        if preferred_date:
            res["use_date"] = preferred_date
        if life_date:
            res["life_date"] = life_date
        return res
