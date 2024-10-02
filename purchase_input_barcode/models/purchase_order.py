# copyright 2022 David BEAL @ Akretion
# copyright 2024 David Palanca @ Grupo Isonor

from odoo import models


class PurchaseOrderLine(models.Model):
    _name = "purchase.order.line"
    _inherit = ["purchase.order.line", "product.barcode.line.mixin"]


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def action_purchase_line_barcode(self, barcode):
        """Create a purchase line according barcode information"""
        self.ensure_one()
        self.env["purchase.order.line"].with_context(
            order_id=self.id, company_id=self.company_id.id
        )._process_barcode_on_product_line(barcode)
