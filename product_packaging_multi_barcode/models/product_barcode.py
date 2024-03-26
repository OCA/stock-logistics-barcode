# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductBarcode(models.Model):
    _inherit = "product.barcode"

    packaging_id = fields.Many2one(
        comodel_name="product.packaging",
        string="Packaging",
        ondelete="cascade",
    )

    display_product_id = fields.Many2one(
        string="Display Product",
        comodel_name="product.product",
        compute="_compute_display_product",
        store=True,
        readonly=False,
        ondelete="cascade",
    )

    @api.depends("product_id", "packaging_id")
    def _compute_display_product(self):
        for rec in self:
            rec.display_product_id = rec.product_id or rec.packaging_id.product_id

    @api.constrains("packaging_id", "product_id")
    def _check_not_define_product_and_packaging(self):
        for record in self:
            if record.packaging_id and record.product_id:
                raise ValidationError(
                    _(
                        "A packaging already uses the barcode or the barcode "
                        "is already assigned to product(s)"
                    )
                )

    @api.constrains("name")
    def _check_duplicates(self):
        """Override this method to change the error messages"""
        for record in self:
            barcode = self.search(
                [("id", "!=", record.id), ("name", "=", record.name)], limit=1
            )
            # by default barcode 'shared' between all company (no ir.rule)
            # so we may not have the access right on the product and packaging
            # note: if you do not want to share the barcode between company
            # you just need to add a custom ir.rule
            if barcode:
                if barcode.sudo().product_id:
                    product = barcode.sudo().product_id
                    raise ValidationError(
                        _(
                            'The Barcode "%(barcode_name)s" already exists for '
                            'product "%(product_name)s" in the company %(company_name)s',
                            barcode_name=record.name,
                            product_name=product.name,
                            company_name=product.company_id.name,
                        )
                    )
                elif barcode.sudo().packaging_id:
                    packaging = barcode.sudo().packaging_id
                    raise ValidationError(
                        _(
                            'The Barcode "%(barcode_name)s" already exists for '
                            'packaging "%(name)s" in the company %(company_name)s.',
                            barcode_name=record.name,
                            name=packaging.name,
                            company_name=packaging.company_id.name or "",
                        )
                    )
