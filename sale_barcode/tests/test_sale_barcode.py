from odoo.exceptions import UserError
from odoo.tests import TransactionCase


class Test(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_input_line(self):
        self.env = self.env(context=dict(self.env.context, tracking_disable=True))
        barcode = "010101"
        product = self.env["product.product"].create(
            {
                "name": "sale barcode product test",
                "barcode": barcode,
            }
        )
        sale = self.env.ref("sale.sale_order_3")
        sale.action_sale_order_line_barcode(barcode)
        self.assertIn(product, sale.order_line.mapped("product_id"))
        invalid_barcode = "123123"
        with self.assertRaises(UserError):
            sale.action_sale_order_line_barcode(invalid_barcode)
