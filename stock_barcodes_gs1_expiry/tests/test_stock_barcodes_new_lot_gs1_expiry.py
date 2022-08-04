# Copyright 2108-2019 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import datetime

from odoo.addons.stock_barcodes_gs1.tests.test_stock_barcodes_new_lot_gs1 import (
    TestStockBarcodesNewLotGS1,
)


class TestStockBarcodesNewLotGS1Expiry(TestStockBarcodesNewLotGS1):
    def setUp(self):
        super().setUp()
        # Barcode with use data
        self.gs1_barcode_01_use_date = "01195011015300001519070410AB-123"

    def test_new_lot_gs1_no_lot_expiry(self):
        self.action_barcode_scanned(self.wiz_scan_lot, self.gs1_barcode_01)
        self.action_barcode_scanned(self.wiz_scan_lot, self.gs1_barcode_01)
        self.assertEqual(self.wiz_scan_lot.life_date, datetime(2014, 7, 4, 0, 0))
        self.action_barcode_scanned(self.wiz_scan_lot, self.gs1_barcode_01_use_date)
        self.assertEqual(self.wiz_scan_lot.use_date, datetime(2019, 7, 4, 0, 0))
        wiz_scan = self.env["wiz.stock.barcodes.read.inventory"].create({})
        wiz_product = self.wiz_scan_lot.product_id
        self.wiz_scan_lot.with_context(
            active_model=wiz_scan._name, active_id=wiz_scan.id,
        ).confirm()
        lot = self.env["stock.production.lot"].search(
            [("name", "=", "AB-123"), ("product_id", "=", wiz_product.id)]
        )
        self.assertEqual(lot.life_date, datetime(2014, 7, 4, 0, 0))
        self.assertEqual(lot.use_date, datetime(2019, 7, 4, 0, 0))
