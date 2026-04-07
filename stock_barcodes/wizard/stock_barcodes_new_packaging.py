# Copyright 2026 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class WizStockBarcodesNewPackaing(models.TransientModel):
    _inherit = "barcodes.barcode_events_mixin"
    _name = "wiz.stock.barcodes.new.packaging"
    _description = "Wizard to create new product packaging from barcode scanner"

    product_id = fields.Many2one(comodel_name="product.product", required=True)
    barcode = fields.Char()
    name = fields.Char(required=True)

    def on_barcode_scanned(self, barcode):
        self.barcode = barcode
        self.name = barcode

    def _prepare_packaging_values(self):
        ProductPackaging = self.env["product.packaging"]
        vals = {
            "product_id": self.product_id.id,
            "name": self.name,
            "barcode": self.barcode,
            "company_id": self.product_id.company_id.id,
            "sales": False,
            "purchase": False,
        }
        if "sales" in ProductPackaging:
            vals["sales"] = False
        if "purchase" in ProductPackaging:
            vals["purchase"] = False
        return vals

    def get_scan_wizard(self):
        return self.env[self.env.context["active_model"]].browse(
            self.env.context["active_id"]
        )

    def scan_wizard_action(self):
        if self.env.context.get("active_model") == "wiz.stock.barcodes.read.inventory":
            action = self.env["ir.actions.actions"]._for_xml_id(
                "stock_barcodes.action_stock_barcodes_read_inventory"
            )
        else:
            action = self.env["ir.actions.actions"]._for_xml_id(
                "stock_barcodes.action_stock_barcodes_read_picking"
            )
        wiz_id = self.get_scan_wizard()
        action["res_id"] = wiz_id.id
        return action

    def confirm(self):
        ProductPackaging = self.env["product.packaging"]
        product_packaging = ProductPackaging.search(
            [("product_id", "=", self.product_id.id), ("barcode", "=", self.barcode)]
        )
        if not product_packaging:
            product_packaging = ProductPackaging.create(
                self._prepare_packaging_values()
            )
        # Assign lot created or found to wizard scanning barcode lot_id field
        wiz = self.get_scan_wizard()
        if wiz:
            wiz.packaging_id = product_packaging
        return self.scan_wizard_action()

    def cancel(self):
        return self.scan_wizard_action()
