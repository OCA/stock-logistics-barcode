# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import _, models
from odoo.exceptions import ValidationError


class BarcodeValidation(models.AbstractModel):
    _name = "barcode.validation.mixin"
    _description = "Barcode Validation"

    def _get_validation_barcode_settings(self):
        return {
            "UPCA": self.env.company.barcode_validation_upca,
            "EAN8": self.env.company.barcode_validation_ean8,
            "EAN13": self.env.company.barcode_validation_ean13,
            "Code128": self.env.company.barcode_validation_code128,
            "DataMatrix": self.env.company.barcode_validation_datamatrix,
            "QR": self.env.company.barcode_validation_qrcode,
        }

    def _validate_barcode(self, barcode):
        validation_barcode_settings = self._get_validation_barcode_settings()
        for (
            barcode_type,
            validation_barcode_type,
        ) in validation_barcode_settings.items():
            if validation_barcode_type:
                try:
                    self.env["ir.actions.report"].barcode(barcode_type, barcode)
                except ValueError as e:
                    raise ValidationError(
                        _(
                            "The barcode {barcode} is not a valid {barcode_type} barcode."
                        ).format(barcode=barcode, barcode_type=barcode_type)
                    ) from e
