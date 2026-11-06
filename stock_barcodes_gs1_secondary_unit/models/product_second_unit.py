# Copyright 2018 Tecnativa - Sergio Teruel
# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
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

    @api.constrains("barcode", "active")
    def _check_barcode_uniqueness(self):
        # A scan matching several secondary units identifies none of them
        units = self.filtered(lambda psu: psu.active and psu.barcode)
        if not units:
            return
        same_barcode_units = self.search([("barcode", "in", units.mapped("barcode"))])
        for psu in units:
            duplicate = (same_barcode_units - psu).filtered(
                lambda other, psu=psu: other.barcode == psu.barcode
            )[:1]
            if duplicate:
                raise ValidationError(
                    _(
                        "The barcode %(barcode)s is already used by the secondary "
                        "unit %(unit)s of %(product)s.",
                        barcode=psu.barcode,
                        unit=duplicate.display_name,
                        product=(
                            duplicate.product_id or duplicate.product_tmpl_id
                        ).display_name,
                    )
                )
