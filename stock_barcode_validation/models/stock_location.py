# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import api, models


class StockLocation(models.Model):
    _name = "stock.location"
    _inherit = ["stock.location", "barcode.validation.mixin"]

    @api.constrains("barcode")
    def check_barcode_validation(self):
        for loc in self.filtered("barcode"):
            loc._validate_barcode(loc.barcode)
