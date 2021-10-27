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
                "prefill_counted_quantity": "zero",
            }
        )
        action = self.inventory.action_barcode_scan()
        self.wiz_scan_inventory = self.ScanReadInventory.browse(action["res_id"])

    def test_inventory_wizard_scan_product(self):
        self.wiz_scan_inventory.auto_lot = False
        self.wiz_scan_inventory.manual_entry = False
        self.action_barcode_scanned(self.wiz_scan_inventory, "8480000723208")
        self.assertEqual(len(self.inventory.line_ids), 1.0)
        # Scan product with tracking lot enable
        self.action_barcode_scanned(self.wiz_scan_inventory, "8433281006850")
        self.assertEqual(len(self.inventory.line_ids), 1.0)
        self.assertEqual(
            self.wiz_scan_inventory.message,
            "8433281006850 (Scan Packaging, Product, Lot)",
        )
        # Scan a lot. Increment quantities if scan product or other lot from
        # this produt
        self.action_barcode_scanned(self.wiz_scan_inventory, "8411822222568")
        self.assertEqual(len(self.inventory.line_ids), 2.0)
        self.action_barcode_scanned(self.wiz_scan_inventory, "8433281006850")
        self.assertEqual(len(self.inventory.line_ids), 2.0)
        self.action_barcode_scanned(self.wiz_scan_inventory, "8411822222568")
        inventory_line_lot = self.inventory.line_ids.filtered("prod_lot_id")
        self.assertEqual(inventory_line_lot.product_qty, 2.0)
        self.assertEqual(
            self.wiz_scan_inventory.message,
            "8411822222568 (Scan Packaging, Product, Lot)",
        )

    def test_inventory_wizard_scan_product_manual_entry(self):
        self.wiz_scan_inventory.manual_entry = True
        self.action_barcode_scanned(self.wiz_scan_inventory, "8480000723208")
        self.assertEqual(self.wiz_scan_inventory.product_id, self.product_wo_tracking)
        self.assertEqual(self.wiz_scan_inventory.product_qty, 0.0)
        self.wiz_scan_inventory.product_qty = 12
        self.wiz_scan_inventory.action_confirm()
        self.assertEqual(len(self.inventory.line_ids), 1.0)

    def test_inventory_wizard_remove_last_scan(self):
        self.action_barcode_scanned(self.wiz_scan_inventory, "8480000723208")
        self.assertEqual(len(self.inventory.line_ids), 1.0)
        self.wiz_scan_inventory.action_undo_last_scan()
        self.assertEqual(self.inventory.line_ids.product_qty, 0.0)

    def test_inventory_wizard_scan_product_auto_lot(self):
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

        # Reset inventory lines
        self.wiz_scan_inventory.inventory_id.line_ids.write({"product_qty": 0.0})
        self._reset_inventory_options()
        self.wiz_scan_inventory.flush()
        # Removal strategy FIFO
        self.action_barcode_scanned(self.wiz_scan_inventory, "8433281006850")
        self.wiz_scan_inventory.product_qty = 125.0
        self.wiz_scan_inventory.action_confirm()
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

        self._reset_inventory_options()
        self.wiz_scan_inventory.action_confirm()
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
        self._reset_inventory_options()
        self.wiz_scan_inventory.action_confirm()
        inventory_lines = self.wiz_scan_inventory.inventory_id.line_ids
        line_assigned = inventory_lines.filtered(lambda x: x.product_qty > 0.0)
        self.assertEqual(line_assigned.prod_lot_id, lot_3)
        self.assertEqual(line_assigned.product_qty, 5)

        # Remove quants for this product
        quants = self.StockQuant.search([("product_id", "=", self.product_tracking.id)])
        quants.unlink()
        self.wiz_scan_inventory.inventory_id.line_ids.action_reset_product_qty()
        self.wiz_scan_inventory.lot_id = False
        self.action_barcode_scanned(self.wiz_scan_inventory, "8433281006850")
        self.wiz_scan_inventory.product_qty = 5.0

        self._reset_inventory_options()
        self.wiz_scan_inventory.action_confirm()
        self.assertEqual(
            self.wiz_scan_inventory.message,
            "8433281006850 (There is no lots to assign quantities)",
        )

    def _reset_inventory_options(self):
        self.wiz_scan_inventory.auto_lot = True
        self.wiz_scan_inventory.manual_entry = True
        self.wiz_scan_inventory.option_group_id.option_ids.filtered(
            lambda p: p.field_name == "lot_id"
        ).required = False
