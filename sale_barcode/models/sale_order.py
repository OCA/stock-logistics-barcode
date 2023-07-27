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
        self._update_sol(product)
        return self._prepared_action(product)

    @api.model
    def _product_barcode_search(self, barcode):
        """Returns the found product by barcode"""
        return self.env["product.product"].search([("barcode", "=", barcode)])

    def _update_sol(self, product):
        """Increase qty in SOL or add new line"""
        if product in self.order_line.mapped("product_id"):
            sol_product = self.order_line.filtered(
                lambda p: p.product_id.id == product.id
            )
            sol_product.product_uom_qty = sol_product.product_uom_qty + 1
        else:
            self.order_line = [(0, 0, {"product_id": product.id})]

    @api.model
    def _update_scanned_info(self, data):
        products = self.env["product.product"].browse(list(set(data)))
        scanned_data = ""
        for product in products:
            scanned_data += "{name} : {qty}\n".format(
                name=product.name, qty=data.count(product.id)
            )
        return scanned_data

    def _prepared_action(self, product):
        context = dict(self.env.context or {})
        barcode_scanned = context.get("default_barcode_scanned", "")
        scanned_products = context.get("scanned_products", [])
        scanned_products.append(product.id)
        barcode_scanned = self._update_scanned_info(scanned_products)
        context.update(
            {
                "default_barcode_scanned": barcode_scanned,
                "scanned_products": scanned_products,
            }
        )
        action_values = self.env.ref(
            "sale_barcode.action_sale_order_line_barcode"
        ).read()[0]
        action_values.update({"context": context})
        action = action_values
        return action
