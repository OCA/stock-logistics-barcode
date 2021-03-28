# Copyright 2108-2019 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common

from odoo.addons.stock_barcodes.tests.test_stock_barcodes import TestStockBarcodes


@common.tagged("post_install", "-at_install")
class TestStockBarcodesQuant(TestStockBarcodes):
    def setUp(self):
        super().setUp()
        self.quant_lot_1.write({"barcode": "123456789"})
        self.quant_lot_2 = self.StockQuant.create(
            {
                "product_id": self.product_tracking.id,
                "lot_id": self.lot_1.id,
                "location_id": self.location_2.id,
                "quantity": 100.0,
                "barcode": "123456780",
            }
        )
        self.quant_lot_3 = self.StockQuant.create(
            {
                "product_id": self.product_tracking.id,
                "lot_id": self.lot_1.id,
                "location_id": self.location_1.id,
                "quantity": 100.0,
                "barcode": "123456780",
            }
        )

    def test_wizard_scan_quant_barcode(self):
        self.action_barcode_scanned(self.wiz_scan, "123456789")
        self.assertEqual(self.wiz_scan.product_id, self.product_tracking)
        self.assertEqual(self.wiz_scan.lot_id, self.lot_1)
        self.action_barcode_scanned(self.wiz_scan, "123456780")
        self.assertFalse(self.wiz_scan.location_id)
        self.assertEqual(self.wiz_scan.product_id, self.product_tracking)
        self.assertEqual(self.wiz_scan.lot_id, self.lot_1)
