# Copyright 2018 Tecnativa - Sergio Teruel
# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from odoo.tools.barcode import get_barcode_check_digit


class ProductSecondaryUnit(models.Model):
    _inherit = "product.secondary.unit"

    barcode = fields.Char(
        copy=False,
        index=True,
        compute="_compute_barcode",
        readonly=False,
        store=True,
        help="International Article Number used for product identification.",
    )
    packaging_indicator = fields.Char(
        size=1,
        help="GS1 packaging indicator digit. When set, the barcode is the GTIN-14 "
        "built from this digit, the product barcode and a new check digit.",
    )

    @api.depends("packaging_indicator", "product_id.barcode", "product_tmpl_id.barcode")
    def _compute_barcode(self):
        for psu in self:
            product_barcode = psu.product_id.barcode or psu.product_tmpl_id.barcode
            # GTIN-13 of the item (EAN-8/UPC-A are left padded with zeros)
            item_gtin = (product_barcode or "").zfill(13)[-13:]
            indicator = psu.packaging_indicator or ""
            if not (product_barcode and indicator.isdigit() and item_gtin.isdigit()):
                # Keep the barcode typed by hand
                psu.barcode = psu.barcode
                continue
            # The item check digit is replaced by the one of the GTIN-14
            gtin = indicator + item_gtin[:-1]
            psu.barcode = gtin + str(get_barcode_check_digit(gtin + "0"))
