# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import api, models


class StockLot(models.Model):
    _name = "stock.lot"
    _inherit = ["stock.lot", "barcode.validation.mixin"]

    @api.constrains("name")
    def check_barcode_validation(self):
        for lot in self.filtered("name"):
            lot._validate_barcode(lot.name)
