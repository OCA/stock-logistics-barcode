# Copyright 2023 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class ProductBarcode(models.Model):
    _inherit = "product.barcode"

    @api.constrains("name")
    def _check_duplicates(self):
        for record in self:
            barcodes = self.search(
                [("id", "!=", record.id), ("name", "=", record.name)], limit=1
            )
            if (
                barcodes
                and barcodes.sudo().product_tmpl_id.company_id.id
                == record.product_tmpl_id.company_id.id
            ):
                super()._check_duplicates()
