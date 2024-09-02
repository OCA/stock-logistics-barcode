# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import api, models


class StockPicking(models.Model):
    _name = "stock.picking"
    _inherit = ["stock.picking", "barcode.validation.mixin"]

    @api.constrains("name")
    def check_barcode_validation(self):
        for picking in self.filtered("name"):
            picking._validate_barcode(picking.name)
