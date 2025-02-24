# copyright 2022 David BEAL @ Akretion

from odoo import models


class SaleOrderLine(models.Model):
    _name = "sale.order.line"
    _inherit = ["sale.order.line", "product.barcode.line.mixin"]


class SaleOrder(models.Model):
    _name = "sale.order"
    _inherit = ["sale.order", "barcodes.barcode_events_mixin"]

    def on_barcode_scanned(self, barcode):
        self.process_barcode(barcode)

    def action_sale_line_barcode(self, barcode):
        """Create a sale line according barcode information"""
        self.ensure_one()
        self.process_barcode(barcode)

    def process_barcode(self, barcode):
        barcode = barcode.rstrip()
        line_vals = (
            self.env["sale.order.line"]
            .with_context(order_id=self.id, company_id=self.company_id.id)
            ._process_barcode_on_product_line(barcode)
        )

        product_order_line = self.order_line.filtered(
            lambda x: x.product_id.id == line_vals.get("product_id")
        )[:1]
        sale_barcode_update_existing_line = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(
                "sale_input_barcode.sale_barcode_update_existing_line",
            )
        )

        if product_order_line and sale_barcode_update_existing_line:
            product_order_line.product_uom_qty += 1
        else:
            product_order_line = self.env["sale.order.line"].new(line_vals)
            product_order_line.product_id_change()
            sale_line_vals = product_order_line._convert_to_write(
                product_order_line._cache
            )
            self.write({"order_line": [(0, 0, sale_line_vals)]})
