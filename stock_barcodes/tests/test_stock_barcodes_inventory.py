# Copyright 2108-2019 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.addons.stock_barcodes.tests.test_stock_barcodes import\
    TestStockBarcodes


class TestStockBarcodesInventory(TestStockBarcodes):

    def setUp(self):
        super().setUp()
        self.ScanReadInventory = self.env['wiz.stock.barcodes.read.inventory']
        self.stock_inventory_model = self.env.ref(
            'stock.model_stock_inventory')
        self.inventory = self.StockInventory.create({
            'name': 'Test Inventory',
            'filter': 'partial',
            'location_id': self.stock_location.id,
        })
        vals = self.inventory.action_barcode_scan()
        self.wiz_scan_inventory = self.ScanReadInventory.with_context(
            vals['context']
        ).create({})

    def test_inventory_values(self):
        self.assertEqual(self.wiz_scan_inventory.location_id,
                         self.inventory.location_id)
        self.assertEqual(self.wiz_scan_inventory.res_model_id,
                         self.stock_inventory_model)
        self.assertEqual(self.wiz_scan_inventory.res_id,
                         self.inventory.id)

    def test_inventory_wizard_scan_product(self):
        self.action_barcode_scanned(self.wiz_scan_inventory, '8480000723208')
        self.assertEqual(self.wiz_scan_inventory.product_id,
                         self.product_wo_tracking)
        self.assertEqual(len(self.inventory.line_ids), 1.0)
        self.wiz_scan_inventory.inventory_product_qty = 1.0
        # Scan product with tracking lot enable
        self.action_barcode_scanned(self.wiz_scan_inventory, '8433281006850')
        self.assertEqual(len(self.inventory.line_ids), 1.0)
        self.assertEqual(self.wiz_scan_inventory.message,
                         'Waiting for input lot (8433281006850)')
        # Scan a lot
        self.action_barcode_scanned(self.wiz_scan_inventory, '8411822222568')
        self.assertEqual(len(self.inventory.line_ids), 1.0)
        self.action_barcode_scanned(self.wiz_scan_inventory, '8433281006850')
        self.assertEqual(len(self.inventory.line_ids), 2.0)
        self.assertEqual(self.wiz_scan_inventory.message,
                         'Barcode read correctly (8433281006850)')
        # Scan a package
        self.action_barcode_scanned(self.wiz_scan_inventory, '5420008510489')
        # Package of 5 product units. Already one unit exists
        self.assertEqual(self.inventory.line_ids[:1].product_qty, 6.0)

    def test_inventory_wizard_remove_last_scan(self):
        self.action_barcode_scanned(self.wiz_scan_inventory, '8480000723208')
        self.assertEqual(self.wiz_scan_inventory.product_id,
                         self.product_wo_tracking)
        self.assertEqual(len(self.inventory.line_ids), 1.0)
        self.wiz_scan_inventory.action_remove_last_scan()
        self.assertEqual(self.inventory.line_ids.product_qty, 0.0)
