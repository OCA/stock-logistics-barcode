# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo.exceptions import ValidationError

from odoo.addons.barcode_validation.tests.test_barcode_validation_mixin import (
    TestBarcodeValidationMixin,
)


class TestProductBarcodeValidation(TestBarcodeValidationMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_barcode_validation_product(self):
        """Validate barcode when product is created/updated."""
        self.toggle_barcode_validation(True)
        with self.assertRaises(ValidationError):
            self.env["product.product"].with_company(self.company).create(
                {"name": "Test Product", "barcode": "123Ç"}
            )
        self.toggle_barcode_validation(False)
        test_product = (
            self.env["product.product"]
            .with_company(self.company)
            .create({"name": "Test Product", "barcode": "123Ç"})
        )
        self.assertEqual(test_product.barcode, "123Ç")
        self.toggle_barcode_validation(True)
        with self.assertRaises(ValidationError):
            test_product.write({"barcode": "123ÇÇ"})
        self.toggle_barcode_validation(False)
        test_product.write({"barcode": "123ÇÇ}"})

    def test_barcode_validation_packaging(self):
        """Validate barcode when product packaging is created/updated."""
        self.toggle_barcode_validation(True)
        product = (
            self.env["product.product"]
            .with_company(self.company)
            .create({"name": "Test product", "type": "consu"})
        )
        with self.assertRaises(ValidationError):
            self.env["product.packaging"].with_company(self.company).create(
                {"name": "Test packaging", "product_id": product.id, "barcode": "123Ç"}
            )
        self.toggle_barcode_validation(False)
        test_packaging = (
            self.env["product.packaging"]
            .with_company(self.company)
            .create(
                {"name": "Test Product", "product_id": product.id, "barcode": "123Ç"}
            )
        )
        self.assertEqual(test_packaging.barcode, "123Ç")
        self.toggle_barcode_validation(True)
        with self.assertRaises(ValidationError):
            test_packaging.write({"barcode": "123ÇÇ}"})
        self.toggle_barcode_validation(False)
        test_packaging.write({"barcode": "123ÇÇ}"})
