# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.es>
# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.es>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo.tests.common import SavepointCase, tagged


@tagged("post_install", "-at_install")
class TestStockBarcodesSupplierInfo(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.StockInventory = cls.env["stock.inventory"]
        cls.Product = cls.env["product.product"]
        cls.WizScanRead = cls.env["wiz.stock.barcodes.read"]
        cls.company = cls.env.user.company_id
        cls.ScanReadInventory = cls.env["wiz.stock.barcodes.read.inventory"]
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.inventory = cls.StockInventory.create(
            {
                "name": "Test Inventory",
                "location_ids": [(6, 0, cls.stock_location.ids)],
            }
        )
        vals = cls.inventory.action_barcode_scan()
        cls.wiz_scan_inventory = cls.ScanReadInventory.with_context(
            vals["context"]
        ).create({})

    def action_barcode_scanned(self, wizard, barcode):
        wizard._barcode_scanned = barcode
        wizard._on_barcode_scanned()

    def test_stock_barcodes_supplierinfo_product_with_barcode(self):
        self.product1 = self.Product.create(
            {
                "name": "Product test",
                "type": "product",
                "tracking": "none",
                "barcode": "987654321",
                "seller_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "1",
                            "barcode": "",
                        },
                    )
                ],
            }
        )

        self.action_barcode_scanned(self.wiz_scan_inventory, "987654321")
        self.assertEqual(self.wiz_scan_inventory.product_id, self.product1)
        self.assertEqual(len(self.inventory.line_ids), 1.0)
        self.wiz_scan_inventory.inventory_product_qty = 1.0

    def test_stock_barcodes_supplierinfo_seller_with_barcode(self):
        self.product2 = self.Product.create(
            {
                "name": "Product 2",
                "type": "product",
                "tracking": "none",
                "barcode": "",
                "seller_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "1",
                            "barcode": "123456789",
                        },
                    )
                ],
            }
        )
        self.action_barcode_scanned(self.wiz_scan_inventory, "123456789")
        self.assertEqual(
            self.wiz_scan_inventory.message,
            "Barcode: 123456789 (Barcode read correctly)",
        )

    def test_stock_barcodes_supplierinfo_seller_with_incorrect_barcode(self):
        self.product2 = self.Product.create(
            {
                "name": "Product 2",
                "type": "product",
                "tracking": "none",
                "barcode": "987654321",
                "seller_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "1",
                            "barcode": "123456789",
                        },
                    )
                ],
            }
        )
        self.action_barcode_scanned(self.wiz_scan_inventory, "999999999")
        self.assertEqual(
            self.wiz_scan_inventory.message,
            "Barcode: 999999999 (Barcode not found)",
        )

    def test_stock_barcodes_supplierinfo_seller_with_incorrect_barcode2(self):
        self.product2 = self.Product.create(
            {
                "name": "Product 3",
                "type": "product",
                "tracking": "none",
                "barcode": "987654321",
                "seller_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "1",
                            "barcode": "123456789",
                        },
                    )
                ],
            }
        )
        self.product3 = self.Product.create(
            {
                "name": "Product 4",
                "type": "product",
                "tracking": "none",
                "barcode": "123456789",
                "seller_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "2",
                            "barcode": "",
                        },
                    )
                ],
            }
        )
        self.action_barcode_scanned(self.wiz_scan_inventory, "123456789")
        self.assertEqual(
            self.wiz_scan_inventory.product_id.name,
            "Product 4",
        )
