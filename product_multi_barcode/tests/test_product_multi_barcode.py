# © 2016 Pedro M. Baeza
# © 2018 Xavier Jimenez (QubiQ)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import Command
from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged

from ..hooks import post_init_hook


@tagged("post_install", "-at_install")
class TestProductMultiBarcode(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Product 1
        cls.product = cls.env["product.product"]
        cls.product_1 = cls.product.create({"name": "Test product 1"})
        cls.valid_barcode_1 = "1234567890128"
        cls.valid_barcode2_1 = "0123456789012"
        # Product 2
        cls.product_2 = cls.product.create({"name": "Test product 2"})
        cls.valid_barcode_2 = "9780471117094"
        cls.valid_barcode2_2 = "4006381333931"
        # Product 3
        cls.product_tmpl_id = cls.env["product.template"].create(
            {"name": "Test product template"}
        )
        cls.product_3 = cls.product.create({"name": "Test product 3"})
        cls.valid_barcode_3 = "9780471999094"
        cls.valid_barcode_3_1 = "9780471170094"
        cls.valid_barcode_3_2 = "9755632170094"
        cls.valid_barcode_4 = "9720456999094"
        cls.valid_barcode_4_1 = "9700075170094"
        # Product Barcode
        cls.barcode = cls.env["product.barcode"]
        cls.barcode_id = cls.barcode.create(
            {
                "name": cls.valid_barcode_3,
                "product_id": cls.product_3.id,
            }
        )

    def test_set_main_barcode(self):
        self.product_1.barcode = self.valid_barcode_1
        self.assertEqual(len(self.product_1.barcode_ids), 1)
        self.assertEqual(self.product_1.barcode_ids.name, self.product_1.barcode)

    def test_set_incorrect_barcode(self):
        self.product_1.barcode = self.valid_barcode_1
        # Insert duplicated EAN13
        with self.assertRaisesRegex(
            ValidationError,
            f'The Barcode "{self.valid_barcode_1}" '
            f'already exists for product "{self.product_1.name}"',
        ):
            self.product_1.barcode_ids = [
                Command.create({"name": self.valid_barcode_1})
            ]

    def test_post_init_hook(self):
        self.env.cr.execute(
            """
            UPDATE product_product
            SET barcode = %s
            WHERE id = %s""",
            (self.valid_barcode_1, self.product_1.id),
        )
        post_init_hook(self.env)
        self.product_1.invalidate_recordset()
        self.assertEqual(len(self.product_1.barcode_ids), 1)
        self.assertEqual(self.product_1.barcode_ids.name, self.valid_barcode_1)

    def test_search(self):
        self.product_1.barcode_ids = [
            Command.create({"name": self.valid_barcode_1}),
            Command.create({"name": self.valid_barcode2_1}),
        ]
        self.product_2.barcode_ids = [
            Command.create({"name": self.valid_barcode_2}),
            Command.create({"name": self.valid_barcode2_2}),
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

    def test_compute_product(self):
        self.barcode_id.product_id = False
        self.assertFalse(self.barcode_id.product_id)
        self.barcode_id._compute_product()
        self.assertTrue(self.barcode_id.product_id)
        self.assertEqual(self.barcode_id.product_id, self.product_3)

    def test_inverse_barcode(self):
        self.product_3.barcode_ids = [Command.clear()]
        self.assertFalse(self.product_3.barcode_ids)
        self.product_3.barcode = self.valid_barcode_3_2
        self.product_3.barcode_ids = [
            Command.create({"name": self.valid_barcode_3}),
            Command.create({"name": self.valid_barcode_3_1}),
        ]
        self.product_3._inverse_barcode()
        self.assertEqual(self.product_3.barcode_ids[0].name, self.valid_barcode_3_2)
        self.product_3.barcode_ids = [Command.clear()]
        self.product_3.barcode = False
        self.product_3._inverse_barcode()
        self.assertFalse(self.product_3.barcode_ids)

    def test_inverse_barcode_unlink(self):
        self.product_3.barcode_ids = [
            Command.create({"name": self.valid_barcode_4}),
            Command.create({"name": self.valid_barcode_4_1}),
        ]
        self.product_3.barcode = False
        self.product_3._inverse_barcode()
        self.assertFalse(self.product_3.barcode_ids)
