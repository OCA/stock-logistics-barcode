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
        self.assertIn(
            "Barcode reader - Test Inventory - ",
            self.wiz_scan_inventory.display_name,
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

    def testinventory_wizard_scan_product_auto_lot(self):
        # Prepare more data
        lot_2 = self.StockProductionLot.create(
            {
                "name": "8411822222578",
                "product_id": self.product_tracking.id,
                "company_id": self.company.id,
            }
        )
        lot_3 = self.StockProductionLot.create(
            {
                "name": "8411822222588",
                "product_id": self.product_tracking.id,
                "company_id": self.company.id,
            }
        )
        quant_lot_2 = self.StockQuant.create(
            {
                "product_id": self.product_tracking.id,
                "lot_id": lot_2.id,
                "location_id": self.stock_location.id,
                "quantity": 15.0,
            }
        )
        quant_lot_3 = self.StockQuant.create(
            {
                "product_id": self.product_tracking.id,
                "lot_id": lot_3.id,
                "location_id": self.stock_location.id,
                "quantity": 10.0,
            }
        )
        self.quant_lot_1.in_date = "2021-01-01"
        quant_lot_2.in_date = "2021-01-05"
        quant_lot_3.in_date = "2021-01-06"
        # Scan product with tracking lot enable
        self.action_barcode_scanned(self.wiz_scan_inventory, "8433281006850")
        self.assertEqual(
            self.wiz_scan_inventory.message,
            "Barcode: 8433281006850 (Waiting for input lot)",
        )

        self.wiz_scan_inventory.auto_lot = True
        self.wiz_scan_inventory.manual_entry = True
        # Removal strategy FIFO
        self.action_barcode_scanned(self.wiz_scan_inventory, "8433281006850")
        self.wiz_scan_inventory.product_qty = 125.0
        self.wiz_scan_inventory.action_manual_entry()
        inventory_lines = self.wiz_scan_inventory.inventory_id.line_ids
        self.assertEqual(inventory_lines[0].product_qty, 100.00)
        self.assertEqual(inventory_lines[1].product_qty, 15.00)
        self.assertEqual(inventory_lines[2].product_qty, 10.00)

        # Removal strategy FIFO
        # Read more quantities than total quants in stock. The extra quantity
        # should be assigned to last lot.
        self.wiz_scan_inventory.inventory_id.line_ids.action_reset_product_qty()
        self.action_barcode_scanned(self.wiz_scan_inventory, "8433281006850")
        self.wiz_scan_inventory.product_qty = 150.0
        self.wiz_scan_inventory.action_manual_entry()
        inventory_lines = self.wiz_scan_inventory.inventory_id.line_ids
        line_assigned = inventory_lines.filtered(lambda x: x.prod_lot_id == lot_3)
        self.assertEqual(line_assigned.product_qty, 35.0)

        # Removal strategy LIFO
        # Read 5.0 quantities and these should be assigned to last lot
        self.wiz_scan_inventory.inventory_id.line_ids.action_reset_product_qty()
        self.wiz_scan_inventory.lot_id = False
        self.product_tracking.categ_id.removal_strategy_id = self.env.ref(
            "stock.removal_lifo"
        )
        self.action_barcode_scanned(self.wiz_scan_inventory, "8433281006850")
        self.wiz_scan_inventory.product_qty = 5.0
        self.wiz_scan_inventory.action_manual_entry()
        inventory_lines = self.wiz_scan_inventory.inventory_id.line_ids
        line_assigned = inventory_lines.filtered(lambda x: x.product_qty > 0.0)
        self.assertEqual(line_assigned.prod_lot_id, lot_3)
        self.assertEqual(line_assigned.product_qty, 5)

        # Barcode read OK
        self.assertEqual(
            self.wiz_scan_inventory.message, "Barcode: 8433281006850 (Manual entry OK)"
        )

        # Remove quants for this product
        quants = self.StockQuant.search([("product_id", "=", self.product_tracking.id)])
        quants.unlink()
        self.wiz_scan_inventory.inventory_id.line_ids.action_reset_product_qty()
        self.wiz_scan_inventory.lot_id = False
        self.action_barcode_scanned(self.wiz_scan_inventory, "8433281006850")
        self.wiz_scan_inventory.product_qty = 5.0
        self.wiz_scan_inventory.action_manual_entry()
        self.assertEqual(
            self.wiz_scan_inventory.message,
            "Barcode: 8433281006850 (There is no lots to assign quantities)",
        )

    def test_inventory_wizard_auto_lot_default_value(self):
        # Company auto lot default value False
        self.assertFalse(self.wiz_scan_inventory.auto_lot)
        self.env.user.company_id.stock_barcodes_inventory_auto_lot = True
        vals = self.inventory.action_barcode_scan()
        wiz_scan_inventory = self.ScanReadInventory.with_context(
            vals["context"]
        ).create({})
        self.assertTrue(wiz_scan_inventory)

    def test_inventory_wizard_onchanges(self):
        self.wiz_scan_inventory.lot_id = self.lot_1
        self.wiz_scan_inventory._onchange_lot_id()
        self.assertFalse(self.wiz_scan_inventory.auto_lot)
        self.wiz_scan_inventory.product_id = self.product_tracking
        self.wiz_scan_inventory._onchange_product_id()
        self.assertEqual(
            self.wiz_scan_inventory.auto_lot,
            bool(self.wiz_scan_inventory._default_auto_lot()),
        )
