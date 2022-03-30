# Copyright 2019 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import _, api, fields, models


class WizStockBarcodesRead(models.AbstractModel):
    _inherit = "wiz.stock.barcodes.read"

    product_tmpl_id = fields.Many2one(
        comodel_name="product.template", related="product_id.product_tmpl_id",
    )
    secondary_uom_id = fields.Many2one(
        comodel_name="product.secondary.unit", string="Secondary uom",
    )
    secondary_uom_qty = fields.Float(
        string="Secondary UOM Qty", digits="Product Unit of Measure"
    )
    secondary_single_qty = fields.Float(
        string="Secondary single Qty", digits="Product Unit of Measure"
    )

    @api.onchange("secondary_uom_id", "secondary_uom_qty", "secondary_single_qty")
    def onchange_secondary_uom_qty(self):
        self.product_qty = (
            self.secondary_uom_qty * self.secondary_uom_id.factor
        ) + self.secondary_single_qty

    def action_secondary_uom_scaned_post(self, secondary_uom):
        self.secondary_uom_id = secondary_uom
        if self.product_id != secondary_uom.product_tmpl_id.product_variant_id:
            self.lot_id = False
        self.product_id = secondary_uom.product_tmpl_id.product_variant_id
        self.secondary_uom_qty = 0.0 if self.manual_entry else 1.0
        self.product_qty = secondary_uom.factor * self.secondary_uom_qty

    def _prepare_scan_log_values(self, log_detail=False):
        vals = super()._prepare_scan_log_values(log_detail=log_detail)
        vals.update(
            {
                "secondary_uom_id": self.secondary_uom_id.id,
                "secondary_uom_qty": self.secondary_uom_qty,
            }
        )
        return vals

    def reset_qty(self):
        res = super().reset_qty()
        self.secondary_uom_qty = 0
        return res

    def process_barcode_package(self, package_barcode, processed):
        secondary_uom = self.env["product.secondary.unit"].search(
            self._barcode_domain(package_barcode)
        )
        if not secondary_uom:
            self._set_messagge_info(
                "not_found", _("Barcode for product secondary uom not found")
            )
            return super().process_barcode_package(package_barcode, processed)
        else:
            if len(secondary_uom) > 1:
                self._set_messagge_info(
                    "more_match", _("More than one secondary uom found")
                )
                return False
            self.action_secondary_uom_scaned_post(secondary_uom)

    @api.onchange("product_id")
    def onchange_product_id(self):
        super().onchange_product_id()
        self.secondary_uom_id = self.product_id.stock_secondary_uom_id
