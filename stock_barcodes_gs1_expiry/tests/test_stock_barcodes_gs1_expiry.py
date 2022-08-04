# Copyright 2108-2019 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime

from odoo.addons.stock_barcodes_gs1.tests.test_stock_barcodes_gs1 import (
    TestStockBarcodesGS1,
)


class TestStockBarcodesGS1Expiry(TestStockBarcodesGS1):
    def setUp(self):
        super().setUp()
        # Barcode with expiry data
        self.gs1_barcode_01 = "01195011015300001714070410AB-123"
        self.gs1_barcode_01_use_date = "01195011015300001519070410AB-123"

    def test_wizard_scan_gs1_expiry_life_date(self):
        self.product_wo_tracking_gs1.tracking = "lot"
        # Scanning barcode with life date data
        self.wiz_scan.manual_entry = True
        self.action_barcode_scanned(self.wiz_scan, self.gs1_barcode_01)
        self.assertEqual(self.wiz_scan.lot_id.life_date, datetime(2014, 7, 4, 0, 0))

    def test_wizard_scan_gs1_expiry_use_date(self):
        self.product_wo_tracking_gs1.tracking = "lot"
        # Scanning barcode with use date data
        self.wiz_scan.manual_entry = True
        self.action_barcode_scanned(self.wiz_scan, self.gs1_barcode_01_use_date)
        self.assertEqual(self.wiz_scan.lot_id.use_date, datetime(2019, 7, 4, 0, 0))
