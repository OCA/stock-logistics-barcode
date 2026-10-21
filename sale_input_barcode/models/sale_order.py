# copyright 2022 David BEAL @ Akretion

from odoo import Command, api, fields, models
from odoo.fields import Domain


class SaleOrderLine(models.Model):
    _name = "sale.order.line"
    _inherit = ("sale.order.line", "product.barcode.line.mixin")

    def _get_barcode_product_domain(self):
        return super()._get_barcode_product_domain() & Domain("sale_ok", "=", True)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    # Same mechanism as `barcodes.barcode_events_mixin`, removed in 20.0
    _barcode_scanned = fields.Char(
        "Barcode Scanned", help="Value of the last barcode scanned.", store=False
    )

    @api.onchange("_barcode_scanned")
    def _on_barcode_scanned(self):
        barcode = self._barcode_scanned
        if barcode:
            self._barcode_scanned = ""
            return self.on_barcode_scanned(barcode)

    def on_barcode_scanned(self, barcode):
        self.process_barcode(barcode)

    def process_barcode(self, barcode):
        barcode = barcode.rstrip()
        line_vals = (
            self.env["sale.order.line"]
            .with_context(company_id=self.company_id.id)
            ._process_barcode_on_product_line(barcode)
        )

        product_order_line = self.order_line.filtered(
            lambda x: (
                x.product_id.id == line_vals.get("product_id")
                and x.product_uom_id.id == line_vals.get("product_uom_id")
            )
        )[:1]
        sale_barcode_update_existing_line = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_bool("sale_input_barcode.sale_barcode_update_existing_line")
        )

        if product_order_line and sale_barcode_update_existing_line:
            product_order_line.product_uom_qty += 1
        else:
            self.write({"order_line": [Command.create(line_vals)]})
