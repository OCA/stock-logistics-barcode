# Copyright 2023 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class ProductBarcode(models.Model):
    _inherit = "product.barcode"

    @api.constrains("name")
    def _check_duplicates(self):
        existing_codes = self.env["product.barcode"]
        for record in self.sudo():
            barcode = self.search(
                [("id", "!=", record.id), ("name", "=", record.name)], limit=1
            )
            if barcode and (
                not record.product_id.company_id
                or (barcode.product_id.company_id == record.product_id.company_id)
            ):
                existing_codes |= record
        if existing_codes:
            super(ProductBarcode, existing_codes)._check_duplicates()
