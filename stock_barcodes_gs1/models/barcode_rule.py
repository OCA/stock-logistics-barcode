# Copyright 2019 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class BarcodeRule(models.Model):
    _inherit = "barcode.rule"

    use_weight_as_unit = fields.Boolean()
