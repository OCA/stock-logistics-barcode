# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    barcode_validation_upca = fields.Boolean(
        related="company_id.barcode_validation_upca", readonly=False
    )
    barcode_validation_ean8 = fields.Boolean(
        related="company_id.barcode_validation_ean8", readonly=False
    )
    barcode_validation_ean13 = fields.Boolean(
        related="company_id.barcode_validation_ean13", readonly=False
    )
    barcode_validation_code128 = fields.Boolean(
        related="company_id.barcode_validation_code128", readonly=False
    )
    barcode_validation_datamatrix = fields.Boolean(
        related="company_id.barcode_validation_datamatrix", readonly=False
    )
    barcode_validation_qrcode = fields.Boolean(
        related="company_id.barcode_validation_qrcode", readonly=False
    )
