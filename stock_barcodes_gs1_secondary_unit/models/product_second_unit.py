# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


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
        help="Barcode prefix, used to generate EAN-14 from EAN-13 product barcode when "
        "first digit is used to define distinct packages.",
    )

    @api.depends("packaging_indicator", "product_id.barcode", "product_tmpl_id.barcode")
    def _compute_barcode(self):
        actions_report_obj = self.env["ir.actions.report"]
        for psu in self:
            p_barcode = psu.product_id.barcode or psu.product_tmpl_id.barcode
            if p_barcode and psu.packaging_indicator:
                new_ean = psu.packaging_indicator + p_barcode
                digit_control = actions_report_obj.get_barcode_check_digit(new_ean)
                psu.barcode = new_ean[0:-1] + str(digit_control)
