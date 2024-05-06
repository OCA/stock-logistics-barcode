# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import api, models


class StockMoveLine(models.Model):
    _name = "stock.move.line"
    _inherit = ["stock.move.line", "barcode.validation.mixin"]

    @api.constrains("lot_name")
    def check_barcode_validation(self):
        for sml in self.filtered("lot_name"):
            sml._validate_barcode(sml.lot_name)
