# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import fields, models


class ConfigSettings(models.Model):
    _inherit = "res.company"

    barcode_validation_upca = fields.Boolean()
    barcode_validation_ean8 = fields.Boolean()
    barcode_validation_ean13 = fields.Boolean()
    barcode_validation_code128 = fields.Boolean()
    barcode_validation_datamatrix = fields.Boolean()
    barcode_validation_qrcode = fields.Boolean()
