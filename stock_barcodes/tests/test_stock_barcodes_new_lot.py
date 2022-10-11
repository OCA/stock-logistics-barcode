# Copyright 2108-2019 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests.common import tagged

from .test_stock_barcodes_picking import TestStockBarcodesPicking


@tagged("post_install", "-at_install")
class TestStockBarcodesNewLot(TestStockBarcodesPicking):
    def setUp(self):
        super().setUp()
        self.ScanReadLot = self.env["wiz.stock.barcodes.new.lot"]
        self.wiz_scan_lot = self.ScanReadLot.new()

    def test_new_lot(self):
        self.action_barcode_scanned(self.wiz_scan_lot, "8433281006850")
        self.assertEqual(self.wiz_scan_lot.product_id, self.product_tracking)
        self.action_barcode_scanned(self.wiz_scan_lot, "8433281xy6850")
        self.assertEqual(self.wiz_scan_lot.lot_name, "8433281xy6850")
        self.wiz_scan_lot.with_context(
            active_model=self.wiz_scan._name,
            active_id=self.wiz_scan.id,
        ).confirm()
        self.assertEqual(self.wiz_scan_lot.lot_name, self.wiz_scan.lot_id.name)
