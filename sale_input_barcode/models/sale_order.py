# copyright 2022 David BEAL @ Akretion

from odoo import models


class SaleOrderLine(models.Model):
    _name = "sale.order.line"
    _inherit = ["sale.order.line", "product.barcode.line.mixin"]


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_sale_line_barcode(self, barcode):
        """Create a sale line according barcode information"""
        self.ensure_one()
        self.env["sale.order.line"].with_context(
            order_id=self.id, company_id=self.company_id.id
        )._process_barcode_on_product_line(barcode)
