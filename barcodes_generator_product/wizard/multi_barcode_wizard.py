# Copyright (C) 2022 Akretion (<http://www.akretion.com>).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class BarcodeMultipleGeneratorWizard(models.TransientModel):
    _name = "barcode.multiple.generator.wizard"
    _description = "Barcode Multiple Generator Wizard"

    product_ids = fields.Many2many(
        comodel_name="product.product",
        string="Products",
    )
    barcode_rule_id = fields.Many2one(
        string="Barcode Rule",
        readonly=False,
        comodel_name="barcode.rule",
        domain=[
            ("generate_model", "=", "product.product"),
            ("generate_automate", "=", True),
        ],
    )
    barcode_base = fields.Integer(
        readonly=False,
        string="Barcode Base start with",
    )
    generate_type = fields.Selection(
        string="Generate Type",
        related="barcode_rule_id.generate_type",
        readonly=True,
    )
    product_barcode_exception = fields.Html(
        readonly=True, compute="_compute_product_barcode_exception"
    )

    ignored_products = fields.Char(
        string="Ignored Products",
    )

    @api.depends("product_ids.barcode")
    def _compute_product_barcode_exception(self):
        message = """
        <b>The following products already have a barcode, they will be ignored:</b><br />
        """
        for rec in self:
            product_with_barcodes = [
                prod.name for prod in rec.product_ids if prod.barcode
            ]
            rec.product_barcode_exception = False
            if rec.ignored_products:
                message += rec.ignored_products
                message += "<br />"
            if product_with_barcodes:
                message += " - ".join(product_with_barcodes)
                rec.product_barcode_exception = message

    def generate_multi_barcode(self):
        product_without_barcodes = [
            prod for prod in self.product_ids if not prod.barcode
        ]
        for count, product in enumerate(product_without_barcodes):
            product.barcode_rule_id = self.barcode_rule_id.id
            if self.generate_type == "sequence":
                product.generate_base()
            else:
                product.barcode_base = self.barcode_base + count
            product.generate_barcode()
