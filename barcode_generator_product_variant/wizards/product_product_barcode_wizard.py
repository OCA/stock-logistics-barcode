from odoo import api, fields, models


class ProductProductBarcodeWizard(models.TransientModel):
    _name = "product.product.barcode.wizard"
    _description = "Wizard to manage barcode generation "
    "for variants of a product"

    def _default_barcode_rule_id(self):
        return self.env["barcode.rule"].search(
            [("is_default", "=", True), ("generate_model", "=", "product.product")],
            limit=1,
        )

    product_tmpl_id = fields.Many2one(
        "product.template", required=True, string="Product"
    )
    product_ids = fields.Many2many(
        "product.product",
        compute="_compute_product_ids",
        string="Variants",
    )
    barcode_rule_id = fields.Many2one(
        string="Barcode Rule",
        comodel_name="barcode.rule",
        required=True,
        default=_default_barcode_rule_id,
        domain="""[
            ('generate_model', '=', 'product.product'),
            ('generate_type', '=', 'sequence'),
            ]""",
    )

    @api.depends("product_tmpl_id")
    def _compute_product_ids(self):
        for wizard in self:
            wizard.product_ids = wizard.mapped(
                "product_tmpl_id.product_variant_ids"
            ).filtered(lambda x: not x.barcode)

    def action_generate_barcodes(self):
        self.ensure_one()
        self.product_ids.write({"barcode_rule_id": self.barcode_rule_id.id})
        self.product_ids.filtered(lambda x: not x.barcode_base).generate_base()
        self.product_ids.generate_barcode()
