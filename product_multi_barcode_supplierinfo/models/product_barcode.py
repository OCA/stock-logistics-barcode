# Copyright 2022 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import fields, models


class ProductBarcode(models.Model):
    _inherit = "product.barcode"

    product_variant_count = fields.Integer(
        "Variant Count", related="product_tmpl_id.product_variant_count"
    )

    supplier_id = fields.Many2one(comodel_name="res.partner", readonly=True)
