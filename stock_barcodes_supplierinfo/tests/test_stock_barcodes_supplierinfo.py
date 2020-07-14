
from odoo.addons.stock_barcodes.tests.\
    test_stock_barcodes import TestStockBarcodes


class TestStockBarcodesSupplierInfo(TestStockBarcodes):

    def setUp(self):
        super().setUp()
        self.supplier_barcode = '8411822222569'

    def test_stock_barcodes_supplierinfo(self):
        self.action_barcode_scanned(self.wiz_scan, self.lot_1.name)
        # check scanning lot is still working
        self.assertEqual(self.wiz_scan.lot_id.name, self.lot_1.name)
        self.assertEqual(
            self.wiz_scan.message, 'Barcode: 8411822222568 (Barcode read correctly)')
        self.action_barcode_scanned(self.wiz_scan, self.supplier_barcode)
        self.assertEqual(
            self.wiz_scan.message, 'Barcode: 8411822222569 (Barcode not found)')
        self.product_tracking.seller_ids = [(0, 0, {
            'name': self.env.ref('base.res_partner_12').id,
            'barcode': self.supplier_barcode,
        })]
        self.action_barcode_scanned(self.wiz_scan, self.supplier_barcode)
        self.assertEqual(
            self.wiz_scan.message, 'Barcode: 8411822222569 (Barcode read correctly)')
