from odoo import fields, models


class BarcodeRule(models.Model):
    _inherit = "barcode.rule"

    use_weight_as_unit = fields.Boolean()
