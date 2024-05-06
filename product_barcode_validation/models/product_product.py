# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import api, models


class Product(models.Model):
    _name = "product.product"
    _inherit = ["product.product", "barcode.validation.mixin"]

    @api.constrains("barcode")
    def check_barcode_validation(self):
        for product in self.filtered("barcode"):
            product._validate_barcode(product.barcode)
