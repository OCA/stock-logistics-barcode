
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime

from odoo.addons.stock_barcodes_gs1.tests.test_stock_barcodes_gs1 import (
    TestStockBarcodesGS1,
)


class TestStockBarcodesGS1NetWeight(TestStockBarcodesGS1):
    def setUp(self):
        super().setUp()
        # Barcode with net weight
        self.gs1_barcode_01 = "01195011015300003100123456"
        self.gs1_barcode_02 = "01195011015300003101123456"
        self.gs1_barcode_03 = "01195011015300003102123456"
        self.gs1_barcode_04 = "01195011015300003103123456"
        self.gs1_barcode_05 = "01195011015300003104123456"
        self.gs1_barcode_06 = "01195011015300003105123456"

    def test_wizard_scan_gs1_expiry_life_date(self):
        self.product_wo_tracking_gs1.tracking = "lot"
        # Scanning barcode with net weight data
        self.action_barcode_scanned(self.wiz_scan, self.gs1_barcode_01)
        self.assertEqual(self.wiz_scan.lot_id.weight, float(123456))
        
        self.action_barcode_scanned(self.wiz_scan, self.gs1_barcode_02)
        self.assertEqual(self.wiz_scan.lot_id.weight, float(12345.6))
        
        self.action_barcode_scanned(self.wiz_scan, self.gs1_barcode_03)
        self.assertEqual(self.wiz_scan.lot_id.weight, float(1234.56))
        
        self.action_barcode_scanned(self.wiz_scan, self.gs1_barcode_04)
        self.assertEqual(self.wiz_scan.lot_id.weight, float(123.456))

        self.action_barcode_scanned(self.wiz_scan, self.gs1_barcode_05)
        self.assertEqual(self.wiz_scan.lot_id.weight, float(12.3456))
        
        self.action_barcode_scanned(self.wiz_scan, self.gs1_barcode_06)
        self.assertEqual(self.wiz_scan.lot_id.weight, float(1.23456))
