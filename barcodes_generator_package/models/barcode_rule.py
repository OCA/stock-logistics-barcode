# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class BarcodeRule(models.Model):
    _inherit = "barcode.rule"

    generate_model = fields.Selection(
        selection_add=[("product.packaging", "Product Packaging")],
        ondelete={"product.packaging": "cascade"},
    )
