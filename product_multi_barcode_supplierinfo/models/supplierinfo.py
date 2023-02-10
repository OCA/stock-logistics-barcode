# Copyright 2022 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SupplierInfo(models.Model):
    _inherit = "product.supplierinfo"

    barcode_id = fields.Many2one(comodel_name="product.barcode")

    barcode = fields.Char(
        compute="_compute_barcode_name",
        inverse="_inverse_barcode_field",
        readonly=False,
        store=True,
    )

    @api.depends("barcode_id.name")
    def _compute_barcode_name(self):
        for rec in self:
            if rec.barcode_id:
                rec.barcode = rec.barcode_id.name
            else:
                rec.barcode = ""

    def _inverse_barcode_field(self):
        for supplier_info in self:
            barcode = self.env["product.barcode"].search(
                [("name", "=", supplier_info.barcode)]
            )
            if not supplier_info.barcode_id:
                if not barcode and supplier_info.barcode:
                    supplier_info.barcode_id = supplier_info.barcode_id.create(
                        {"name": supplier_info.barcode}
                    )
                elif barcode:
                    supplier_info.barcode_id = barcode
            else:
                supplier_info.barcode_id.name = supplier_info.barcode
            supplier_info.barcode_id.supplier_id = supplier_info.name
            supplier_info.barcode_id.product_tmpl_id = supplier_info.product_tmpl_id
            if supplier_info.product_tmpl_id.product_variant_count > 1:
                supplier_info.barcode_id.product_id = supplier_info.product_id

    @api.constrains("barcode")
    def check_barcode(self):
        for rec in self:
            if (
                rec.product_tmpl_id.product_variant_count > 1
                and rec.barcode
                and (not rec.product_id)
            ):
                raise ValidationError(
                    _("You have to specify variant for the supplierinfo with barcode")
                )

    def unlink_product_barcode(self):
        self.ensure_one()
        product_barcode_id = self.env["product.barcode"].search(
            [
                ("product_tmpl_id", "=", self.product_tmpl_id.id),
                ("name", "=", self.barcode_id.name),
            ]
        )
        if product_barcode_id:
            product_barcode_id.unlink()

    def unlink(self):
        for rec in self:
            if rec.barcode:
                rec.unlink_product_barcode()
        super().unlink()
