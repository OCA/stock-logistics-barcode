from odoo.exceptions import UserError
from odoo.tests import TransactionCase


class TestBarcode(TransactionCase):
    def setUp(self):
        super().setUp()
        self.barcode = "010101"
        self.product = self.env["product.product"].create(
            {
                "name": "sale barcode product test",
                "barcode": self.barcode,
            }
        )
        self.sale = self.env.ref("sale.sale_order_3")

    def test_input_line(self):
        self.env = self.env(context=dict(self.env.context, tracking_disable=True))
        self.sale.action_sale_order_line_barcode(self.barcode)
        self.assertIn(self.product, self.sale.order_line.mapped("product_id"))
        self.sale.action_sale_order_line_barcode(self.barcode)
        self.assertEqual(
            2,
            self.sale.order_line.filtered(
                lambda p: p.product_id.id == self.product.id
            ).product_uom_qty,
            "Must be equal 2",
        )
        invalid_barcode = "123123"
        with self.assertRaises(UserError):
            self.sale.action_sale_order_line_barcode(invalid_barcode)

    def test_update_scanned_info(self):
        products = [self.product.id, self.product.id]
        scanned_data = self.sale._update_scanned_info(products)
        prepared_data = "{name} : {qty}\n".format(
            name=self.product.name, qty=products.count(self.product.id)
        )
        self.assertEqual(prepared_data, scanned_data, "Must be equal")

    def test_prepared_action(self):
        action = self.sale._prepared_action(self.product)
        prepared_data = "{name} : {qty}\n".format(name=self.product.name, qty=1)
        context = action["context"]
        scanned_data = context.get("default_barcode_scanned", "")
        self.assertEqual(prepared_data, scanned_data, "Must be equal")
        scanned_products = context.get("scanned_products", [])
        self.assertIn(
            self.product.id, scanned_products, msg="The product id must be in the sheet"
        )
