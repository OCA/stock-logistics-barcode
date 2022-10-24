# Copyright (C) 2014-Today GRAP (http://www.grap.coop)
# Copyright (C) 2016-Today La Louve (http://www.lalouve.net)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    # Related to display product product information if is_product_variant
    barcode_rule_id = fields.Many2one(
        string="Barcode Rule",
        related="product_variant_ids.barcode_rule_id",
        comodel_name="barcode.rule",
        readonly=False,
    )

    barcode_base = fields.Integer(
        string="Barcode Base",
        related="product_variant_ids.barcode_base",
        readonly=False,
    )

    generate_type = fields.Selection(
        string="Generate Type",
        related="product_variant_ids.barcode_rule_id.generate_type",
        readonly=True,
    )

    # View Section
    def generate_base(self):
        self.product_variant_ids.generate_base()

    def generate_barcode(self):
        self.ensure_one()
        self.product_variant_ids.generate_barcode()

    @api.onchange("barcode_rule_id")
    def onchange_barcode_rule_id(self):
        self.generate_type = self.barcode_rule_id.generate_type

    # Overload Section
    @api.model_create_multi
    def create(self, vals_list):
        # this is needed to set given values to first variant after creation
        # these fields should be moved to product as lead to confusion
        # (Ref. product module feature in Odoo Core)
        result = self
        for vals in vals_list:
            template = super().create(vals)
            related_vals = {}
            for field in ["barcode_rule_id", "barcode_base"]:
                if vals.get(field, False):
                    related_vals[field] = vals[field]
            if related_vals:
                template.write(related_vals)
            result |= template
        return result
