from odoo import _, api, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_sale_order_line_barcode(self, barcode):
        """Create a sale line according barcode information"""
        self.ensure_one()
        product = self._product_barcode_search(barcode)
        if not product:
            raise UserError(_("There is no product with such a barcode"))
        self.order_line = [(0, 0, {"product_id": product.id})]
        return {"type": "ir.actions.act_window_close"}

    @api.model
    def _product_barcode_search(self, barcode):
        """Returns the found product by barcode"""
        return self.env["product.product"].search([("barcode", "=", barcode)])
