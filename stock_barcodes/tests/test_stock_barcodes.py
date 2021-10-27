# Copyright 2108-2019 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestStockBarcodes(TransactionCase):
    def setUp(self):
        super().setUp()

        # Active group_stock_packaging and group_production_lot for user
        group_stock_packaging = self.env.ref("product.group_stock_packaging")
        group_production_lot = self.env.ref("stock.group_production_lot")
        self.env.user.groups_id = [
            (4, group_stock_packaging.id),
            (4, group_production_lot.id),
        ]
        # models
        self.StockLocation = self.env["stock.location"]
        self.StockInventory = self.env["stock.inventory"]
        self.Product = self.env["product.product"]
        self.ProductPackaging = self.env["product.packaging"]
        self.WizScanReadPicking = self.env["wiz.stock.barcodes.read.picking"]
        self.StockProductionLot = self.env["stock.production.lot"]
        self.StockPicking = self.env["stock.picking"]
        self.StockQuant = self.env["stock.quant"]

        self.company = self.env.company

        # Option groups for test
        self.option_group = self._create_barcode_option_group()

        # warehouse and locations
        self.warehouse = self.env.ref("stock.warehouse0")
        self.stock_location = self.env.ref("stock.stock_location_stock")
        self.location_1 = self.StockLocation.create(
            {
                "name": "Test location 1",
                "usage": "internal",
                "location_id": self.stock_location.id,
                "barcode": "8411322222568",
            }
        )
        self.location_2 = self.StockLocation.create(
            {
                "name": "Test location 2",
                "usage": "internal",
                "location_id": self.stock_location.id,
                "barcode": "8470001809032",
            }
        )

        # products
        self.product_wo_tracking = self.Product.create(
            {
                "name": "Product test wo lot tracking",
                "type": "product",
                "tracking": "none",
                "barcode": "8480000723208",
                "packaging_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Box 10 Units",
                            "qty": 10.0,
                            "barcode": "5099206074439",
                        },
                    )
                ],
            }
        )
        self.product_tracking = self.Product.create(
            {
                "name": "Product test with lot tracking",
                "type": "product",
                "tracking": "lot",
                "barcode": "8433281006850",
                "packaging_ids": [
                    (
                        0,
                        0,
                        {"name": "Box 5 Units", "qty": 5.0, "barcode": "5420008510489"},
                    )
                ],
            }
        )
        self.lot_1 = self.StockProductionLot.create(
            {
                "name": "8411822222568",
                "product_id": self.product_tracking.id,
                "company_id": self.company.id,
            }
        )
        self.quant_lot_1 = self.StockQuant.create(
            {
                "product_id": self.product_tracking.id,
                "lot_id": self.lot_1.id,
                "location_id": self.stock_location.id,
                "quantity": 100.0,
            }
        )
        self.wiz_scan = self.WizScanReadPicking.create(
            {"option_group_id": self.option_group.id, "step": 1}
        )

    def _create_barcode_option_group(self):
        return self.env["stock.barcodes.option.group"].create(
            {
                "name": "option group for tests",
                "show_scan_log": True,
                "option_ids": [
                    (
                        0,
                        0,
                        {
                            "step": 1,
                            "name": "Location",
                            "field_name": "location_id",
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
                        },
                    ),
                ],
            }
        )

    def action_barcode_scanned(self, wizard, barcode):
        wizard._barcode_scanned = barcode
        wizard._on_barcode_scanned()

    def test_wizard_scan_location(self):
        self.action_barcode_scanned(self.wiz_scan, "8411322222568")
        self.assertEqual(self.wiz_scan.location_id, self.location_1)

    def test_wizard_scan_product(self):
        self.wiz_scan.location_id = self.location_1
        self.wiz_scan.action_show_step()
        self.action_barcode_scanned(self.wiz_scan, "8480000723208")
        self.assertEqual(self.wiz_scan.product_id, self.product_wo_tracking)
        self.assertEqual(self.wiz_scan.product_qty, 1.0)

    def test_wizard_scan_product_manual_entry(self):
        # Test manual entry
        self.wiz_scan.manual_entry = True
        self.wiz_scan.location_id = self.location_1
        self.wiz_scan.action_show_step()
        self.action_barcode_scanned(self.wiz_scan, "8480000723208")
        self.assertEqual(self.wiz_scan.product_qty, 0.0)
        self.wiz_scan.product_qty = 50.0

    def test_wizard_scan_package(self):
        self.wiz_scan.location_id = self.location_1
        self.wiz_scan.action_show_step()
        self.action_barcode_scanned(self.wiz_scan, "5420008510489")
        self.assertEqual(self.wiz_scan.product_id, self.product_tracking)
        self.assertEqual(self.wiz_scan.product_qty, 5.0)
        self.assertEqual(
            self.wiz_scan.packaging_id, self.product_tracking.packaging_ids
        )

        # Manual entry
        self.wiz_scan.manual_entry = True
        self.action_barcode_scanned(self.wiz_scan, "5420008510489")
        self.assertEqual(self.wiz_scan.packaging_qty, 0.0)
        self.wiz_scan.packaging_qty = 3.0
        self.wiz_scan.onchange_packaging_qty()
        self.assertEqual(self.wiz_scan.product_qty, 15.0)
        self.wiz_scan.manual_entry = False

        # Force more than one package with the same lot
        self.product_wo_tracking.packaging_ids.barcode = "5420008510489"
        self.action_barcode_scanned(self.wiz_scan, "5420008510489")
        self.assertEqual(
            self.wiz_scan.message,
            "5420008510489 (More than one package found)",
        )

    def test_wizard_scan_lot(self):
        self.wiz_scan.location_id = self.location_1.id
        self.wiz_scan.action_show_step()
        self.action_barcode_scanned(self.wiz_scan, "8411822222568")
        # Lot found for one product, so product_id is filled
        self.assertTrue(self.wiz_scan.product_id)
        self.action_barcode_scanned(self.wiz_scan, "8433281006850")
        self.action_barcode_scanned(self.wiz_scan, "8411822222568")
        self.assertEqual(self.wiz_scan.lot_id, self.lot_1)
        # After scan other product, set wizard lot to False
        self.action_barcode_scanned(self.wiz_scan, "8480000723208")
        self.assertFalse(self.wiz_scan.lot_id)

    def test_wizard_scan_not_found(self):
        self.action_barcode_scanned(self.wiz_scan, "84118xxx22568")
        self.assertEqual(
            self.wiz_scan.message,
            "84118xxx22568 (Barcode not found with this screen values)",
        )

    def test_wizard_remove_last_scan(self):
        self.assertTrue(self.wiz_scan.action_undo_last_scan())

    def test_wiz_clean_lot(self):
        self.wiz_scan.location_id = self.location_1.id
        self.wiz_scan.action_show_step()
        self.action_barcode_scanned(self.wiz_scan, "8433281006850")
        self.action_barcode_scanned(self.wiz_scan, "8411822222568")
        self.wiz_scan.action_clean_lot()
        self.assertFalse(self.wiz_scan.lot_id)
