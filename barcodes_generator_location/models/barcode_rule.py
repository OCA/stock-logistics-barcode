# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class BarcodeRule(models.Model):
    _inherit = "barcode.rule"

    generate_model = fields.Selection(
        selection_add=[("stock.location", "Stock Location")],
    )
