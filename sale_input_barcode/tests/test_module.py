# © 2022 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import UserError
from odoo.tests import TransactionCase


class Test(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_input_line(self):
        self.env = self.env(context=dict(self.env.context, tracking_disable=True))
        barcode = "01034009338167591714050010B04059A\x1d310500638515140501"
        product = self.env["product.product"].create(
            {
                "name": "barcode test",
                "barcode": barcode[2:16],
            }
        )
        sale = self.env.ref("sale.sale_order_3")
        sale.action_sale_line_barcode(barcode)
        self.assertIn(product, sale.order_line.mapped("product_id"))

    def test_no_product_found(self):
        barcode = "01034009338167591714050010B04059A\x1d310500638515140501"
        sale = self.env.ref("sale.sale_order_3")
        with self.assertRaises(UserError):
            sale.action_sale_line_barcode(barcode)
