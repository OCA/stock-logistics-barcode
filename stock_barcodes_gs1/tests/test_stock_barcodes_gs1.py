# Copyright 2108-2019 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common

from odoo.addons.stock_barcodes.tests.test_stock_barcodes import TestStockBarcodes


@common.tagged("post_install", "-at_install")
class TestStockBarcodesGS1(TestStockBarcodes):
    def setUp(self):
        super().setUp()
        # Barcode for packaging and lot
        self.gs1_barcode_01_product = "0119501101530000"
        self.gs1_barcode_01_lot = "1714070410AB-123"
        self.gs1_separator = self.env.user.gs1_barcode_separator or "\x1D"
        self.gs1_barcode_unit_01 = self.gs1_separator + "371"
        self.gs1_barcode_unit_02 = self.gs1_separator + "372"
        self.gs1_barcode_01 = self.gs1_barcode_01_product + self.gs1_barcode_01_lot
        self.gs1_barcode_01_not_found = "011xxx11015300001714070410AB-123"
        self.gs1_barcode_01_not_lot = "01195011015300001714070410AB-124"
        # Barcode for product and quantities
        self.gs1_barcode_02 = "0207010001234567150410183724"
        self.gs1_barcode_02_not_found = "020xxx0001234567150410183724"
        # Barcode not processed
        self.gs1_barcode_01_not_processed = (
            "01993167101234533101002620130" "5041710ABC123214145354"
        )

        self.product_wo_tracking_gs1 = self.product_wo_tracking.with_context({}).copy(
            {"barcode": "07010001234567"}
        )
        self.product_tracking_gs1 = self.product_tracking.with_context({}).copy()
        self.packaging_gs1 = self.ProductPackaging.create(
            {
                "product_id": self.product_wo_tracking_gs1.id,
                "name": "Box 10 Units",
                "qty": 10.0,
                "barcode": "19501101530000",
            }
        )
        # Set location to avoid crash tests
        self.wiz_scan.location_id = self.location_1

    def test_wizard_scan_gs1_package_multi(self):
        self.packaging_gs1.product_id = self.product_tracking_gs1
        lot = self.StockProductionLot.create(
            {
                "name": "AB-123",
                "product_id": self.product_tracking_gs1.id,
                "company_id": self.company.id,
            }
        )
        self.action_barcode_scanned(self.wiz_scan, self.gs1_barcode_01_product)
        self.assertEqual(self.wiz_scan.product_id, self.product_tracking_gs1)
        self.assertEqual(self.wiz_scan.packaging_id, self.packaging_gs1)
        self.assertFalse(self.wiz_scan.lot_id)
        self.assertEqual(self.wiz_scan.packaging_qty, 1)
        self.assertEqual(self.wiz_scan.product_qty, 10)
        self.action_barcode_scanned(self.wiz_scan, self.gs1_barcode_01_lot)
        self.assertEqual(self.wiz_scan.product_id, self.product_tracking_gs1)
        self.assertEqual(self.wiz_scan.packaging_id, self.packaging_gs1)
        self.assertEqual(self.wiz_scan.lot_id, lot)
        self.assertEqual(self.wiz_scan.packaging_qty, 1)
        self.assertEqual(self.wiz_scan.product_qty, 10)

    def test_wizard_scan_gs1_package(self):
        self.action_barcode_scanned(self.wiz_scan, self.gs1_barcode_01)
        self.assertEqual(self.wiz_scan.packaging_id, self.packaging_gs1)
        # Scan no exist packaging
        self.action_barcode_scanned(self.wiz_scan, self.gs1_barcode_01_not_found)
        self.assertEqual(
            self.wiz_scan.message,
            "011xxx11015300001714070410AB-123 "
            "(Barcode for product packaging not found)",
        )
        # Scan packaging barcode with more than one package
        self.packaging_gs1.with_context({}).copy({"barcode": "19501101530000"})
        self.action_barcode_scanned(self.wiz_scan, self.gs1_barcode_01)
        self.assertEqual(
            self.wiz_scan.message,
            "01195011015300001714070410AB-123 " "(More than one package found)",
        )

    def test_wizard_scan_gs1_package_units(self):
        self.action_barcode_scanned(self.wiz_scan, self.gs1_barcode_01)
        self.assertEqual(self.wiz_scan.packaging_id, self.packaging_gs1)
        self.assertEqual(self.wiz_scan.product_qty, 10)
        self.action_barcode_scanned(
            self.wiz_scan, self.gs1_barcode_01 + self.gs1_barcode_unit_01
        )
        self.assertEqual(self.wiz_scan.packaging_id, self.packaging_gs1)
        self.assertEqual(self.wiz_scan.product_qty, 10)
        self.action_barcode_scanned(
            self.wiz_scan, self.gs1_barcode_01 + self.gs1_barcode_unit_02
        )
        self.assertEqual(self.wiz_scan.packaging_id, self.packaging_gs1)
        self.assertEqual(self.wiz_scan.product_qty, 20)

    def test_wizard_scan_gs1_product(self):
        self.wiz_scan.location_id = self.location_1
        self.action_barcode_scanned(self.wiz_scan, self.gs1_barcode_02)
        self.assertEqual(self.wiz_scan.product_id, self.product_wo_tracking_gs1)
        self.assertEqual(self.wiz_scan.product_qty, 24)
        # Scan non exists product
        self.action_barcode_scanned(self.wiz_scan, self.gs1_barcode_02_not_found)
        self.assertEqual(
            self.wiz_scan.message,
            "020xxx0001234567150410183724 (Barcode for product packaging not found)",
        )

    def test_wizard_scan_gs1_product_as_packaging(self):
        self.product_wo_tracking_gs1.barcode = "X07010001234567Xg"
        self.action_barcode_scanned(self.wiz_scan, self.gs1_barcode_02)
        self.assertEqual(
            self.wiz_scan.message,
            "0207010001234567150410183724 " "(Barcode for product packaging not found)",
        )
        self.ProductPackaging.create(
            {
                "product_id": self.product_wo_tracking_gs1.id,
                "name": "Barcode as package",
                "qty": 2.0,
                "barcode": "07010001234567",
            }
        )
        self.action_barcode_scanned(self.wiz_scan, self.gs1_barcode_02)
        self.assertEqual(self.wiz_scan.product_id, self.product_wo_tracking_gs1)
        self.assertEqual(self.wiz_scan.product_qty, 48)

    def test_wizard_scan_gs1_lot(self):
        self.packaging_gs1.product_id = self.product_tracking_gs1
        lot = self.StockProductionLot.create(
            {
                "name": "AB-123",
                "product_id": self.product_tracking_gs1.id,
                "company_id": self.company.id,
            }
        )
        self.action_barcode_scanned(self.wiz_scan, self.gs1_barcode_01)
        self.assertEqual(self.wiz_scan.lot_id, lot)
        self.assertEqual(
            self.wiz_scan.message,
            "01195011015300001714070410AB-123 " "(Barcode read correctly)",
        )
        self.action_barcode_scanned(self.wiz_scan, self.gs1_barcode_01_not_lot)
        self.assertEqual(self.wiz_scan.lot_id.name, "AB-124")

    def test_wizard_scan_gs1_not_found(self):
        self.action_barcode_scanned(self.wiz_scan, self.gs1_barcode_01_not_processed)
        self.assertEqual(
            self.wiz_scan.message,
            "0199316710123453310100262013050417"
            "10ABC123214145354 (Barcode for product packaging "
            "not found)",
        )
