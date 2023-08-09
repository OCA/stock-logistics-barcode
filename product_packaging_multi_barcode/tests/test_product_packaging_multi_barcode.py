# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged

from ..hooks import post_init_hook


@tagged("post_install", "-at_install")
class TestProductPackagingMultiBarcode(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Product
        cls.product = cls.env["product.product"]
        cls.product = cls.product.create({"name": "Test product"})
        cls.valid_barcode_1 = "1234567890128"
        # Product packaging
        cls.product_packaging_1 = cls.env["product.packaging"].create(
            {
                "name": "Test product packaging 1",
                "product_id": cls.product.id,
                "qty": 3,
            }
        )

    def test_set_main_barcode(self):
        self.product_packaging_1.barcode = self.valid_barcode_1
        self.assertEqual(len(self.product_packaging_1.barcode_ids), 1)
        self.assertEqual(
            self.product_packaging_1.barcode_ids.name, self.product_packaging_1.barcode
        )

    def test_set_incorrect_barcode(self):
        self.product_packaging_1.barcode = self.valid_barcode_1
        # Insert duplicated EAN13
        expected_message = (
            'The Barcode "{}" already exists for ' 'packaging "{}" in the company .'
        ).format(self.valid_barcode_1, self.product_packaging_1.name)

        with self.assertRaisesRegex(ValidationError, expected_message):
            self.product_packaging_1.barcode_ids = [
                (0, 0, {"name": self.valid_barcode_1})
            ]

    def test_barcode_product_and_packaging(self):
        self.product.barcode = self.valid_barcode_1
        # Insert duplicated EAN13
        expected_message = (
            'The Barcode "{}" already exists for ' 'product "{}" in the company .'
        ).format(self.valid_barcode_1, self.product.name)

        with self.assertRaisesRegex(ValidationError, expected_message):
            self.product_packaging_1.barcode_ids = [
                (0, 0, {"name": self.valid_barcode_1})
            ]

    def test_post_init_hook(self):
        self.env.cr.execute(
            """
            UPDATE product_packaging
            SET barcode = %s
            WHERE id = %s""",
            (self.valid_barcode_1, self.product_packaging_1.id),
        )
        post_init_hook(self.env.cr, self.registry)
        self.product_packaging_1.invalidate_recordset()
        self.assertEqual(len(self.product_packaging_1.barcode_ids), 1)
        self.assertEqual(
            self.product_packaging_1.barcode_ids.name, self.valid_barcode_1
        )
