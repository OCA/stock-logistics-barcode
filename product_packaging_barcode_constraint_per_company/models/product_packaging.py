# Copyright 2024 Akretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class ProductPackaging(models.Model):
    _inherit = "product.packaging"

    # replace the unique SQL constraint
    _sql_constraints = [
        (
            "barcode_uniq",
            "unique(barcode, company_id)",
            "A barcode can only be assigned to one packaging per company.",
        ),
    ]

    @api.constrains("barcode")
    def _check_barcode_uniqueness(self):
        return super(
            ProductPackaging,
            self.with_context(search_only_in_pkg_company=self.company_id.ids),
        )._check_barcode_uniqueness()
