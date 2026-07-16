# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, models
from odoo.exceptions import ValidationError

from ..tools.barcode_validation import is_valid_gtin_barcode


class ProductProduct(models.Model):
    _name = "product.product"
    _inherit = ["product.product", "product.barcode.mixin"]

    @api.constrains("barcode")
    def _check_barcode_gtin(self):
        company = self.env.company
        for product in self.filtered(
            lambda p: (not p.company_id and company.enforce_gtin_barcodes)
            or p.company_id.enforce_gtin_barcodes
        ):
            barcode = product.barcode
            if not barcode:
                continue

            if not is_valid_gtin_barcode(barcode):
                raise ValidationError(
                    _(
                        "The barcode '%(barcode)s' on product '%(name)s' is not "
                        "a valid GTIN.",
                        barcode=barcode,
                        name=product.display_name,
                    )
                )
