# Copyright 2108-2019 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common

from odoo.addons.mail.tests.common import MailCommon
from odoo.addons.stock_barcodes.tests.test_stock_barcodes import TestStockBarcodes


@common.tagged("post_install", "-at_install")
class TestStockBarcodesGS1(TestStockBarcodes, MailCommon):
    # pylint: disable=W8121
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        gs1_nomenclature = cls.env.ref(
            "barcodes_gs1_nomenclature.default_gs1_nomenclature"
        )
        # Barcode for packaging and lot
        cls.gs1_barcode_01_product = "0118410525244930"
        cls.gs1_barcode_01_lot = "1714070410AB-123"
        cls.gs1_separator = gs1_nomenclature.gs1_separator_fnc1 or "\x1D"
        cls.gs1_barcode_unit_01 = cls.gs1_separator + "301"
        cls.gs1_barcode_unit_02 = cls.gs1_separator + "302"
        cls.gs1_barcode_unit_03 = cls.gs1_separator + "373"
        cls.gs1_barcode_01 = cls.gs1_barcode_01_product + cls.gs1_barcode_01_lot
        cls.gs1_barcode_01_not_found = "011xxx11015300001714070410AB-123"
        cls.gs1_barcode_01_not_lot = "01184105252449301714070410AB-124"
        # Barcode for product and quantities
        cls.gs1_barcode_02 = "0228411144100307"
        cls.gs1_barcode_02_not_found = "0228501110080433"
        # Barcode not processed
        cls.gs1_barcode_01_not_processed = (
            "01993167101234533101002620130" "5041710ABC123214145354"
        )
        cls.product_wo_tracking_gs1 = cls.product_wo_tracking.with_context({}).copy(
            {"barcode": "28411144100307", "name": "product_wo_tracking_gs1"}
        )
        cls.product_tracking_gs1 = cls.product_tracking.with_context({}).copy(
            {"name": "product_tracking_gs1"}
        )
        cls.packaging_gs1 = cls.ProductPackaging.create(
            {
                "product_id": cls.product_wo_tracking_gs1.id,
                "name": "Box 10 Units",
                "qty": 10.0,
                "barcode": "18410525244930",
            }
        )
        # Set location to avoid crash tests
        cls.wiz_scan.location_id = cls.location_1
        cls.wiz_scan.option_group_id.display_notification = True

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

    def _assert_barcode_notification(
        self, message, title="GS-1 code", sticky=True, type="danger"
    ):
        self.assertBusNotifications(
            [[self.cr.dbname, "stock_barcodes-{}".format(self.wiz_scan.id)]],
            [
                {
                    "type": "stock_barcodes_notify-{}".format(self.wiz_scan.id),
                    "payload": {
                        "message": message,
                        "type": type,
                        "sticky": sticky,
                        "title": title,
                    },
                }
            ],
            check_unique=False,
        )

    def test_wizard_scan_gs1_package(self):
        self.action_barcode_scanned(self.wiz_scan, self.gs1_barcode_01)
        self.assertEqual(self.wiz_scan.packaging_id, self.packaging_gs1)
        # Scan no exist packaging
        self.action_barcode_scanned(self.wiz_scan, self.gs1_barcode_01_not_found)
        self.assertIn(
            "011xxx11015300001714070410AB-123 "
            "(Barcode not found with this screen values)",
            self.wiz_scan.message,
        )
        # Scan packaging barcode with more than one package
        self.packaging_gs1.with_context({}).copy({"barcode": "18410525244930"})
        self.action_barcode_scanned(self.wiz_scan, self.gs1_barcode_01)
        self._assert_barcode_notification(
            message="18410525244930 (More than one package found)"
        )
        self._assert_barcode_notification(message="(10)AB-123 Not found")

    def test_wizard_scan_gs1_package_units(self):
        self.packaging_gs1.product_id = self.product_tracking_gs1
        # Test AI (01) with AI (30)
        self.action_barcode_scanned(self.wiz_scan, self.gs1_barcode_01)
        self.assertEqual(self.wiz_scan.packaging_id, self.packaging_gs1)
        self.assertEqual(self.wiz_scan.product_qty, 10)
        # Test AI (01) with AI (30)
        self.action_barcode_scanned(
            self.wiz_scan, self.gs1_barcode_01 + self.gs1_barcode_unit_01
        )
        self.assertEqual(self.wiz_scan.packaging_id, self.packaging_gs1)
        self.assertEqual(self.wiz_scan.product_qty, 10)
        # Test AI (01) with AI (30)
        self.action_barcode_scanned(
            self.wiz_scan, self.gs1_barcode_01 + self.gs1_barcode_unit_02
        )
        self.assertEqual(self.wiz_scan.packaging_id, self.packaging_gs1)
        self.assertEqual(self.wiz_scan.product_qty, 20)
        # Test AI (02) with AI (37)
        self.action_barcode_scanned(
            self.wiz_scan, self.gs1_barcode_02 + self.gs1_barcode_unit_03
        )
        self.assertEqual(self.wiz_scan.product_qty, 3)

    def test_wizard_scan_gs1_product(self):
        self.wiz_scan.location_id = self.location_1
        self.action_barcode_scanned(self.wiz_scan, self.gs1_barcode_02)
        self.assertEqual(self.wiz_scan.product_id, self.product_wo_tracking_gs1)
        self.assertEqual(self.wiz_scan.product_qty, 1.0)
        # Scan non exists product
        self.action_barcode_scanned(self.wiz_scan, self.gs1_barcode_02_not_found)
        self._assert_barcode_notification(message="(02)28501110080433 Not found")

    def test_wizard_scan_gs1_product_as_packaging(self):
        self.wiz_scan.location_id = self.location_1.id
        self.wiz_scan.action_show_step()
        self.product_wo_tracking_gs1.barcode = "X28411144100307Xg"
        self.action_barcode_scanned(self.wiz_scan, self.gs1_barcode_02)
        self._assert_barcode_notification(message="(02)28411144100307 Not found")
        self.ProductPackaging.create(
            {
                "product_id": self.product_wo_tracking_gs1.id,
                "name": "Barcode as package",
                "qty": 2.0,
                "barcode": "28411144100307",
            }
        )
        self.action_barcode_scanned(self.wiz_scan, self.gs1_barcode_02)
        self.assertEqual(self.wiz_scan.product_id, self.product_wo_tracking_gs1)
        self.assertEqual(self.wiz_scan.product_qty, 2.0)

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
        self.action_barcode_scanned(self.wiz_scan, self.gs1_barcode_01_not_lot)
        self.assertEqual(self.wiz_scan.lot_name, "AB-124")

    def test_wizard_scan_gs1_not_found(self):
        self.wiz_scan.location_id = self.location_1.id
        self.wiz_scan.action_show_step()
        self.action_barcode_scanned(self.wiz_scan, self.gs1_barcode_01_not_processed)
        self._assert_barcode_notification(message="(01)99316710123453 Not found")
        self._assert_barcode_notification(message="(10)ABC123214145354 Not found")

    def test_wizard_scan_gs1_multi_barcode(self):
        # Create a packaging for product
        product = self.product_tracking.with_context({}).copy()
        packaging_box_24 = self.ProductPackaging.create(
            {
                "product_id": product.id,
                "name": "Box 24 Units",
                "qty": 1,
                "barcode": "08412598002106",
            }
        )
        packaging_pallet_6 = self.ProductPackaging.create(
            {
                "product_id": product.id,
                "name": "Pallet 60 Units",
                "qty": 60,
                "barcode": "384125980801041268",
            }
        )

        option_group = self.env["stock.barcodes.option.group"].create(
            {
                "name": "option group for tests IN GS1",
                "create_lot": True,
                "is_manual_confirm": True,
                "option_ids": [
                    (
                        0,
                        0,
                        {
                            "step": 1,
                            "name": "Location",
                            "field_name": "location_id",
                            "filled_default": True,
                            "to_scan": True,
                            "required": True,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "step": 2,
                            "name": "Product",
                            "field_name": "product_id",
                            "to_scan": True,
                            "required": True,
                            "clean_after_done": True,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "step": 2,
                            "name": "Packaging",
                            "field_name": "packaging_id",
                            "to_scan": True,
                            "required": False,
                            "clean_after_done": True,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "step": 2,
                            "name": "Lot / Serial",
                            "field_name": "lot_id",
                            "to_scan": True,
                            "required": True,
                            "clean_after_done": True,
                        },
                    ),
                ],
            }
        )

        wiz_inventory = self.env["wiz.stock.barcodes.read.inventory"].create(
            {
                "location_id": self.env["stock.warehouse"]
                .search([])[:1]
                .lot_stock_id.id,
                "option_group_id": option_group.id,
                "step": 1,
                "display_read_quant": True,
            }
        )
        self.action_barcode_scanned(wiz_inventory, "010841259800210615240914")
        self.assertEqual(wiz_inventory.packaging_id, packaging_box_24)
        self.assertEqual(wiz_inventory.product_qty, 1.0)

        self.action_barcode_scanned(wiz_inventory, "0038412598080104126810LOTEG01")
        self.assertEqual(wiz_inventory.packaging_id, packaging_pallet_6)
        self.assertEqual(wiz_inventory.product_qty, 60.0)

        self.assertEqual(wiz_inventory.product_id, product)
        self.assertEqual(wiz_inventory.lot_name, "LOTEG01")

        wiz_inventory.action_confirm()
        self.assertEqual(wiz_inventory.inventory_quant_ids.lot_id.name, "LOTEG01")
