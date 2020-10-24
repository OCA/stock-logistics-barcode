
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import datetime

from odoo.addons.stock_barcodes_gs1.tests.test_stock_barcodes_new_lot_gs1 import (
    TestStockBarcodesNewLotGS1,
)


class TestStockBarcodesNewLotGS1Expiry(TestStockBarcodesNewLotGS1):
    def setUp(self):
        super().setUp()
        # Barcode with use data       
        self.gs1_barcode_02 = "0119501101530000310112345610AB-123"

    def test_new_lot_gs1_no_lot_expiry(self):
        self.action_barcode_scanned(self.wiz_scan_lot, self.gs1_barcode_01_use_date)
        self.assertEqual(self.wiz_scan_lot.weight, float(12345.6))
        wiz_scan = self.env["wiz.stock.barcodes.read.inventory"].create({})
        self.wiz_scan_lot.with_context(
            active_model=wiz_scan._name, active_id=wiz_scan.id,
        ).confirm()
        lot = self.env["stock.production.lot"].search(
            [
                ("name", "=", "AB-123"),
                ("product_id", "=", self.wiz_scan_lot.product_id.id),
            ]
        )
        self.assertEqual(lot.weight, float(12345.6))
