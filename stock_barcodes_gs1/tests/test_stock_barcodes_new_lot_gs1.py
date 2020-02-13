# Copyright 2108-2019 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests import common

from odoo.addons.stock_barcodes_gs1.tests.test_stock_barcodes_gs1 import (
    TestStockBarcodesGS1,
)


@common.tagged("post_install", "-at_install")
class TestStockBarcodesNewLotGS1(TestStockBarcodesGS1):
    def setUp(self):
        super().setUp()
        self.ScanReadLot = self.env["wiz.stock.barcodes.new.lot"]
        self.wiz_scan_lot = self.ScanReadLot.new()
        self.gs1_barcode_02_10 = "02174512345678911718112510AAA2701370150"

    def test_new_lot_gs1_package(self):
        self.action_barcode_scanned(self.wiz_scan_lot, self.gs1_barcode_01)
        self.assertEqual(self.wiz_scan_lot.product_id, self.product_wo_tracking_gs1)
        self.assertEqual(self.wiz_scan_lot.lot_name, "AB-123")

    def test_new_lot_gs1_product(self):
        self.product_tracking_gs1.barcode = "17451234567891"
        self.action_barcode_scanned(self.wiz_scan_lot, self.gs1_barcode_02_10)
        self.assertEqual(self.wiz_scan_lot.product_id, self.product_tracking_gs1)
        self.assertEqual(self.wiz_scan_lot.lot_name, "AAA2701370150")

    def test_new_lot_gs1_no_lot(self):
        self.action_barcode_scanned(self.wiz_scan_lot, self.gs1_barcode_02)
        self.assertFalse(self.wiz_scan_lot.product_id)
