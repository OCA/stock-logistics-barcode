# © 2022 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import TransactionCase


class Test(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_input_line(self):
        self.env = self.env(context=dict(self.env.context, tracking_disable=True))
        barcode = "5156000000030"
        product = self.env["product.product"].create(
            {
                "name": "barcode test",
                "barcode": barcode,
            }
        )
        sale = self.env.ref("sale.sale_order_3")
        sale.action_sale_line_barcode(barcode)
        self.assertIn(product, sale.order_line.mapped("product_id"))
