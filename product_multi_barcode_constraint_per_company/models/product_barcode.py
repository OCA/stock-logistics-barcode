# Copyright 2023 Akretion (https://www.akretion.com).
# @author Pierrick Brun <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class ProductBarcode(models.Model):
    _inherit = "product.barcode"

    def _get_duplicates(self, barcodes_to_check):
        self.ensure_one()
        barcodes_to_check = super()._get_duplicates(barcodes_to_check)
        barcode_ids = set()
        for barcode in barcodes_to_check:
            if (
                not barcode.company_id
                or not self.company_id
                or barcode.company_id == self.company_id
            ):
                barcode_ids.add(barcode.id)
        return self.browse(barcode_ids)
