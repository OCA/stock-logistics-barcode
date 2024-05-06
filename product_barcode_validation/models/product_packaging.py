# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import api, models


class ProductPackaging(models.Model):
    _name = "product.packaging"
    _inherit = ["product.packaging", "barcode.validation.mixin"]

    @api.constrains("barcode")
    def check_barcode_validation(self):
        for packaging in self.filtered("barcode"):
            packaging._validate_barcode(packaging.barcode)
