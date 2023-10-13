# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    _sql_constraints = [
        # Replace constraint with same name
        (
            "barcode_uniq",
            "unique(barcode, company_id)",
            "A barcode can only be assigned to one product per company !",
        ),
    ]
