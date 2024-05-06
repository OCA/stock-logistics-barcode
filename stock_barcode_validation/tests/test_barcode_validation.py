# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo.exceptions import ValidationError

from odoo.addons.barcode_validation.tests.test_barcode_validation_mixin import (
    TestBarcodeValidationMixin,
)


class TestStockBarcodeValidation(TestBarcodeValidationMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = (
            cls.env["product.product"]
            .with_company(cls.company)
            .create({"name": "Test product", "type": "product"})
        )
        cls.warehouse = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.company.id)], limit=1
        )
        cls.customer_location = cls.env.ref("stock.stock_location_customers")

    def test_barcode_validation_location(self):
        """Validate barcode when product is created/updated."""
        self.toggle_barcode_validation(True)
        with self.assertRaises(ValidationError):
            self.env["stock.location"].with_company(self.company).create(
                {"name": "Test Location", "barcode": "123Ç"}
            )
        self.toggle_barcode_validation(False)
        test_location = (
            self.env["stock.location"]
            .with_company(self.company)
            .create({"name": "Test Location", "barcode": "123Ç"})
        )
        self.assertEqual(test_location.barcode, "123Ç")
        self.toggle_barcode_validation(True)
        with self.assertRaises(ValidationError):
            test_location.write({"barcode": "123ÇÇ}"})
        self.toggle_barcode_validation(False)
        test_location.write({"barcode": "123ÇÇ"})
        self.assertEqual(test_location.barcode, "123ÇÇ")

    def test_barcode_validation_lot(self):
        """Validate barcode when product is created/updated."""
        self.toggle_barcode_validation(True)
        self.product.tracking = "lot"
        with self.assertRaises(ValidationError):
            self.env["stock.lot"].with_company(self.company).create(
                {"name": "123Ç", "product_id": self.product.id}
            )
        self.toggle_barcode_validation(False)
        test_lot = (
            self.env["stock.lot"]
            .with_company(self.company)
            .create({"name": "123Ç", "product_id": self.product.id})
        )
        self.assertEqual(test_lot.name, "123Ç")
        self.toggle_barcode_validation(True)
        with self.assertRaises(ValidationError):
            test_lot.write({"name": "123ÇÇ}"})
        self.toggle_barcode_validation(False)
        test_lot.write({"name": "123ÇÇ"})
        self.assertEqual(test_lot.name, "123ÇÇ")

    def test_barcode_validation_stock_picking(self):
        """Validate barcode when product is created/updated."""
        self.toggle_barcode_validation(True)
        with self.assertRaises(ValidationError):
            self.env["stock.picking"].with_company(self.company).create(
                {
                    "name": "123Ç",
                    "location_id": self.warehouse.lot_stock_id.id,
                    "location_dest_id": self.customer_location.id,
                    "company_id": self.company.id,
                    "picking_type_id": self.warehouse.out_type_id.id,
                }
            )
        self.toggle_barcode_validation(False)
        test_picking = (
            self.env["stock.picking"]
            .with_company(self.company)
            .create(
                {
                    "name": "123Ç",
                    "location_id": self.warehouse.lot_stock_id.id,
                    "location_dest_id": self.customer_location.id,
                    "company_id": self.company.id,
                    "picking_type_id": self.warehouse.out_type_id.id,
                }
            )
        )
        self.assertEqual(test_picking.name, "123Ç")
        self.toggle_barcode_validation(True)
        with self.assertRaises(ValidationError):
            test_picking.write({"name": "123ÇÇ}"})
        self.toggle_barcode_validation(False)
        test_picking.write({"name": "123ÇÇ"})
        self.assertEqual(test_picking.name, "123ÇÇ")

    def test_barcode_validation_stock_quant_package(self):
        """Validate barcode when product is created/updated."""
        self.toggle_barcode_validation(True)
        with self.assertRaises(ValidationError):
            self.env["stock.quant.package"].with_company(self.company).create(
                {
                    "name": "123Ç",
                }
            )
        self.toggle_barcode_validation(False)
        test_package = (
            self.env["stock.quant.package"]
            .with_company(self.company)
            .create(
                {
                    "name": "123Ç",
                }
            )
        )
        self.assertEqual(test_package.name, "123Ç")
        self.toggle_barcode_validation(True)
        with self.assertRaises(ValidationError):
            test_package.write({"name": "123ÇÇ}"})
        self.toggle_barcode_validation(False)
        test_package.write({"name": "123ÇÇ"})
        self.assertEqual(test_package.name, "123ÇÇ")
