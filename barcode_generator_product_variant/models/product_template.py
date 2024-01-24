from odoo import _, api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    has_missing_barcodes = fields.Boolean(
        compute="_compute_has_missing_barcodes",
        store=True,
    )

    @api.depends("product_variant_ids.barcode")
    def _compute_has_missing_barcodes(self):
        for product in self:
            product.has_missing_barcodes = bool(
                product.product_variant_ids.filtered(lambda x: not x.barcode)
            )

    def action_open_variant_barcode_wizard(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Barcode Generation"),
            "res_model": "product.product.barcode.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                **self._context,
                "default_product_tmpl_id": self.id,
            },
        }
