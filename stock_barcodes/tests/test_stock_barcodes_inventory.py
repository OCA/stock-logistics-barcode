# Copyright 2108-2019 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests.common import tagged

from .test_stock_barcodes import TestStockBarcodes


@tagged("post_install", "-at_install")
class TestStockBarcodesInventory(TestStockBarcodes):
    def setUp(self):
        super().setUp()
        self.ScanReadInventory = self.env["wiz.stock.barcodes.read.inventory"]
        self.stock_inventory_model = self.env.ref("stock.model_stock_inventory")
        self.inventory = self.StockInventory.create(
            {
                "name": "Test Inventory",
                "location_ids": [(6, 0, self.stock_location.ids)],
            }
        )
        vals = self.inventory.action_barcode_scan()
        self.wiz_scan_inventory = self.ScanReadInventory.with_context(
            vals["context"]
        ).create({})

    def test_inventory_values(self):
        self.assertEqual(
            self.wiz_scan_inventory.location_id, self.inventory.location_ids[:1]
        )
        self.assertEqual(
            self.wiz_scan_inventory.res_model_id, self.stock_inventory_model
        )
        self.assertEqual(self.wiz_scan_inventory.res_id, self.inventory.id)
        self.assertEqual(
            self.wiz_scan_inventory.display_name,
            "Barcode reader - Test Inventory - OdooBot",
        )

    def test_inventory_wizard_scan_product(self):
        self.action_barcode_scanned(self.wiz_scan_inventory, "8480000723208")
        self.assertEqual(self.wiz_scan_inventory.product_id, self.product_wo_tracking)
        self.assertEqual(len(self.inventory.line_ids), 1.0)
        self.wiz_scan_inventory.inventory_product_qty = 1.0
        # Scan product with tracking lot enable
        self.action_barcode_scanned(self.wiz_scan_inventory, "8433281006850")
        self.assertEqual(len(self.inventory.line_ids), 1.0)
        self.assertEqual(
            self.wiz_scan_inventory.message,
            "Barcode: 8433281006850 (Waiting for input lot)",
        )
        # Scan a lot. Increment quantities if scan product or other lot from
        # this produt
        self.action_barcode_scanned(self.wiz_scan_inventory, "8411822222568")
        self.assertEqual(len(self.inventory.line_ids), 2.0)
        self.action_barcode_scanned(self.wiz_scan_inventory, "8433281006850")
        self.assertEqual(len(self.inventory.line_ids), 2.0)
        self.action_barcode_scanned(self.wiz_scan_inventory, "8411822222568")
        inventory_line_lot = self.inventory.line_ids.filtered("prod_lot_id")
        self.assertEqual(inventory_line_lot.product_qty, 3.0)
        self.assertEqual(
            self.wiz_scan_inventory.message,
            "Barcode: 8411822222568 (Barcode read correctly)",
        )
        # Scan a package
        self.action_barcode_scanned(self.wiz_scan_inventory, "5420008510489")
        # Package of 5 product units. Already three unit exists
        inventory_line_lot = self.inventory.line_ids.filtered("prod_lot_id")
        self.assertEqual(inventory_line_lot.product_qty, 8.0)

    def test_inventory_wizard_scan_product_manual_entry(self):
        self.wiz_scan_inventory.manual_entry = True
        self.action_barcode_scanned(self.wiz_scan_inventory, "8480000723208")
        self.assertEqual(self.wiz_scan_inventory.product_id, self.product_wo_tracking)
        self.assertEqual(self.wiz_scan_inventory.product_qty, 0.0)
        self.wiz_scan_inventory.product_qty = 12
        self.wiz_scan_inventory.action_manual_entry()
        self.assertEqual(len(self.inventory.line_ids), 1.0)
        self.wiz_scan_inventory.inventory_product_qty = 12.0

    def test_inventory_wizard_remove_last_scan(self):
        self.action_barcode_scanned(self.wiz_scan_inventory, "8480000723208")
        self.assertEqual(self.wiz_scan_inventory.product_id, self.product_wo_tracking)
        self.assertEqual(len(self.inventory.line_ids), 1.0)
        self.wiz_scan_inventory.action_undo_last_scan()
        self.assertEqual(self.inventory.line_ids.product_qty, 0.0)
