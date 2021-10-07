from odoo import models, fields, api, _
from odoo.exceptions import UserError


class Template(models.Model):
    _inherit = "product.template"

    ean13_ids = fields.One2many(
        comodel_name="product.ean13",
        string="EAN13",
        compute="_compute_ean13_ids",
        inverse="_set_ean13_ids"
    )

    @api.depends(
        "product_variant_ids.ean13_ids.sequence", "product_variant_ids.ean13_ids.name"
    )
    def _compute_ean13_ids(self):
        unique_variants = self.filtered(
            lambda template: len(template.product_variant_ids) == 1)
        for template in unique_variants:
            template.ean13_ids = [
                (4, ean.id) for ean in template.product_variant_ids.ean13_ids]
        for template in (self - unique_variants):
            template.ean13_ids = False

    def _set_ean13_ids(self):
        for template in self:
            if len(template.product_variant_ids) > 1:
                raise UserError(_(
                    "Can't set EAN for products with more than 1 variant"))
            if len(template.product_variant_ids) == 1:
                for ean in template.ean13_ids:
                    if not isinstance(ean.id, int):
                        # then it's a "new" record
                        ean.product_id = template.product_variant_ids.id
                        ean.create(ean._convert_to_write(ean._cache))
                # We only need to handle deletion: creation is automatic at
                # template saving
                deleted = template.product_variant_ids.ean13_ids - template.ean13_ids
                deleted.unlink()

    @api.model
    def create(self, vals):
        t = super(Template, self).create(vals)
        if "ean13_ids" in vals:
            t.ean13_ids = vals["ean13_ids"]
        return t
