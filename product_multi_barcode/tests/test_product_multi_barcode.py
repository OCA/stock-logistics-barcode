# © 2016 Pedro M. Baeza
# © 2018 Xavier Jimenez (QubiQ)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase, at_install, post_install

from ..hooks import post_init_hook


@at_install(False)
@post_install(True)
class TestProductMultiBarcode(TransactionCase):
    def setUp(self):
        super(TestProductMultiBarcode, self).setUp()
        # Product 1
        self.product = self.env["product.product"]
        self.product_1 = self.product.create({"name": "Test product 1"})
        self.valid_barcode_1 = "1234567890128"
        self.valid_barcode2_1 = "0123456789012"
        # Product 2
        self.product_2 = self.product.create({"name": "Test product 2"})
        self.valid_barcode_2 = "9780471117094"
        self.valid_barcode2_2 = "4006381333931"

    def test_set_main_barcode(self):
        self.product_1.barcode = self.valid_barcode_1
        self.assertEqual(len(self.product_1.barcode_ids), 1)
        self.assertEqual(self.product_1.barcode_ids.name, self.product_1.barcode)

    def test_set_incorrect_barcode(self):
        self.product_1.barcode = self.valid_barcode_1
        # Insert duplicated EAN13
        with self.assertRaises(Exception):
            self.product_1.barcode_ids = [(0, 0, {"name": self.valid_barcode_1})]

    def test_post_init_hook(self):
        self.env.cr.execute(
            """
            UPDATE product_product
            SET barcode = %s
            WHERE id = %s""",
            (self.valid_barcode_1, self.product_1.id),
        )
        post_init_hook(self.env.cr, self.registry)
        self.product_1.refresh()
        self.assertEqual(len(self.product_1.barcode_ids), 1)
        self.assertEqual(self.product_1.barcode_ids.name, self.valid_barcode_1)

    def test_search(self):
        self.product_1.barcode_ids = [
            (0, 0, {"name": self.valid_barcode_1}),
            (0, 0, {"name": self.valid_barcode2_1}),
        ]
        self.product_2.barcode_ids = [
            (0, 0, {"name": self.valid_barcode_2}),
            (0, 0, {"name": self.valid_barcode2_2}),
        ]
        products = self.product.search([("barcode", "=", self.valid_barcode_1)])
        self.assertEqual(len(products), 1)
        self.assertEqual(products, self.product_1)
        products = self.product.search([("barcode", "=", self.valid_barcode2_1)])
        self.assertEqual(len(products), 1)
        self.assertEqual(products, self.product_1)
        products = self.product.search(
            [
                "|",
                ("barcode", "=", self.valid_barcode2_1),
                ("barcode", "=", self.valid_barcode2_2),
            ]
        )
        self.assertEqual(len(products), 2)
