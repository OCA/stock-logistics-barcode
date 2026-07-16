# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class ProductBarcodeMixin(models.AbstractModel):
    _name = "product.barcode.mixin"
    _description = "Product Barcode Logic Mixin"

    @api.onchange("barcode")
    def _onchange_barcode(self):
        for record in self:
            company = record.company_id or self.env.company
            if (
                company.enforce_gtin_barcodes
                and record.barcode
                and len(record.barcode) == 14
                and record.barcode.startswith("0")
            ):
                record.barcode = record.barcode[1:]
