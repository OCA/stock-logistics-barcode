# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.fields import Domain


class ProductTemplate(models.Model):
    _inherit = "product.template"

    barcode_ids = fields.One2many(
        comodel_name="product.barcode",
        inverse_name="product_tmpl_id",
        string="Barcodes",
    )

    # Barcodes live on the variants: a template with several variants has none
    @api.depends("product_variant_ids.barcode", "product_variant_ids.active")
    def _compute_barcode(self):
        multi_variant = self.filtered(lambda t: len(t.product_variant_ids) > 1)
        multi_variant.barcode = False
        return super(ProductTemplate, self - multi_variant)._compute_barcode()

    def _set_barcode(self):
        multi_variant = self.filtered(lambda t: len(t.product_variant_ids) > 1)
        multi_variant.barcode = False
        return super(ProductTemplate, self - multi_variant)._set_barcode()

    @api.model
    def _search(self, domain, *args, **kwargs):
        # The core barcode uniqueness checks compare the stored template barcode
        if not self.env.context.get("skip_barcode_uniqueness_check"):
            domain = Domain(domain).map_conditions(self._map_barcode_condition)
        return super()._search(domain, *args, **kwargs)

    @api.model
    def _map_barcode_condition(self, condition):
        if condition.field_expr == "barcode":
            return Domain("barcode_ids.name", condition.operator, condition.value)
        return condition
