# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import api, models


class QuantPackage(models.Model):
    _name = "stock.quant.package"
    _inherit = ["stock.quant.package", "barcode.validation.mixin"]

    @api.constrains("name")
    def check_barcode_validation(self):
        for package in self.filtered("name"):
            package._validate_barcode(package.name)
