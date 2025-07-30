# © 2012-2014 Guewen Baconnier (Camptocamp SA)
# © 2015 Roberto Lizana (Trey)
# © 2016 Pedro M. Baeza
# © 2018 Xavier Jimenez (QubiQ)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductBarcode(models.Model):
    _name = "product.barcode"
    _description = "Individual item in a product's barcode list"
    _order = "sequence, id"

    name = fields.Char(
        string="Barcode",
        required=True,
    )
    sequence = fields.Integer(
        default=0,
    )
    product_id = fields.Many2one(
        string="Product",
        comodel_name="product.product",
        compute="_compute_product",
        store=True,
        readonly=False,
        ondelete="cascade",
    )
    product_tmpl_id = fields.Many2one(
        comodel_name="product.template",
        compute="_compute_product_tmpl",
        store=True,
        readonly=False,
        ondelete="cascade",
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        related="product_id.company_id",
        readonly=True,
    )

    @api.depends("product_id")
    def _compute_product_tmpl(self):
        for rec in self.filtered(lambda x: not x.product_tmpl_id and x.product_id):
            rec.product_tmpl_id = rec.product_id.product_tmpl_id

    @api.depends("product_tmpl_id.product_variant_ids")
    def _compute_product(self):
        for rec in self.filtered(
            lambda x: not x.product_id and x.product_tmpl_id.product_variant_ids
        ):
            rec.product_id = rec.product_tmpl_id.product_variant_ids[0]

    def _get_domain_check_duplicates(self):
        return [("id", "not in", self.ids), ("name", "in", self.mapped("name"))]

    def _get_duplicates(self, barcodes_to_check):
        self.ensure_one()
        return barcodes_to_check.filtered(lambda b: b.name == self.name)

    @api.constrains("name")
    def _check_duplicates(self):
        barcodes_to_check = self.sudo().search(self._get_domain_check_duplicates())
        for record in self:
            duplicate = record._get_duplicates(barcodes_to_check)
            if duplicate:
                # by default barcode 'shared' between all company (no ir.rule)
                # so we may not have the access right on the product
                product = duplicate[0].sudo().product_id
                raise ValidationError(
                    _(
                        'The Barcode "%(barcode_name)s" already exists for '
                        'product "%(product_name)s" in the company %(company_name)s'
                    )
                    % dict(
                        barcode_name=record.name,
                        product_name=product.name,
                        company_name=product.company_id.name,
                    )
                )
