
from odoo.addons.stock_barcodes.tests.\
    test_stock_barcodes import TestStockBarcodes


class TestStockBarcodesMultiEan(TestStockBarcodes):

    def setUp(self):
        super().setUp()
        self.extra_ean = '8411822222570'

    def test_stock_barcodes_supplierinfo(self):
        self.action_barcode_scanned(self.wiz_scan, self.lot_1.name)
        # check scanning lot is still working
        self.assertEqual(self.wiz_scan.lot_id.name, self.lot_1.name)
        self.assertEqual(
            self.wiz_scan.message, 'Barcode: 8411822222568 (Barcode read correctly)')
        self.action_barcode_scanned(self.wiz_scan, self.extra_ean)
        self.assertEqual(
            self.wiz_scan.message, 'Barcode: 8411822222570 (Barcode not found)')
        self.product_tracking.ean13_ids = [(0, 0, {
            'name': self.extra_ean,
        })]
        self.action_barcode_scanned(self.wiz_scan, self.extra_ean)
        self.assertEqual(
            self.wiz_scan.message, 'Barcode: 8411822222570 (Barcode read correctly)')
