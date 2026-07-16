# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, models
from odoo.exceptions import ValidationError


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

            # Normalize GTIN-14 with a leading zero down to GTIN-13
            if len(barcode) == 14 and barcode.startswith("0"):
                barcode = barcode[1:]

            if len(barcode) == 8:
                product._check_barcode_gtin_length_and_checksum(barcode, 8)
            elif len(barcode) == 12:
                product._check_barcode_gtin_length_and_checksum(barcode, 12)
            elif len(barcode) == 13:
                product._check_barcode_gtin_length_and_checksum(barcode, 13)
            elif len(barcode) == 14:
                product._check_barcode_gtin_length_and_checksum(barcode, 14)
            else:
                raise ValidationError(
                    _(
                        "The barcode '%(barcode)s' on product '%(name)s' does not "
                        "match any standard GTIN length (8, 12, 13, or 14 digits).",
                        barcode=barcode,
                        name=product.display_name,
                    )
                )

    def _check_barcode_gtin_length_and_checksum(self, barcode, length):
        """Validates digit composition, expected length, and GS1 checksum."""
        self.ensure_one()

        if not barcode.isdigit() or len(barcode) != length:
            raise ValidationError(
                _(
                    "The barcode '%(barcode)s' on product '%(name)s'"
                    " must be exactly %(length)s digits.",
                    barcode=barcode,
                    name=self.display_name,
                    length=length,
                )
            )

        # GS1 Checksum Algorithm (weights alternate 3 and 1 from right to left)
        # The last digit is the checksum digit itself
        digits = [int(char) for char in barcode]
        payload_digits = digits[:-1]
        check_digit = digits[-1]

        # Reversing allows unified index handling across all lengths:
        # Index 0 (1st to the left of checksum) always gets weight 3,
        # index 1 gets weight 1, etc.
        total_sum = sum(
            num * (3 if i % 2 == 0 else 1)
            for i, num in enumerate(reversed(payload_digits))
        )

        if (total_sum + check_digit) % 10 != 0:
            raise ValidationError(
                _(
                    "The barcode '%(barcode)s' on product '%(name)s' "
                    "has an invalid GTIN-%(length)s checksum.",
                    barcode=barcode,
                    name=self.display_name,
                    length=length,
                )
            )
