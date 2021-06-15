# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    barcode_ids = fields.One2many(
        comodel_name="product.barcode",
        inverse_name="product_tmpl_id",
        string="Barcodes",
    )
