# © 2022 David BEAL @ Akretion
# © 2024 David Palanca @ Grupo Isonor
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import TransactionCase


class Test(TransactionCase):

    def test_input_line(self):
        self.env = self.env(context=dict(self.env.context, tracking_disable=True))
        barcode = "01034009338167591714050010B04059A\x1d310500638515140501"
        product = self.env["product.product"].create(
            {
                "name": "barcode test",
                "barcode": barcode[2:16],
            }
        )
        purchase = self.env.ref("purchase.purchase_order_3")
        purchase.action_purchase_line_barcode(barcode)
        self.assertIn(product, purchase.order_line.mapped("product_id"))
