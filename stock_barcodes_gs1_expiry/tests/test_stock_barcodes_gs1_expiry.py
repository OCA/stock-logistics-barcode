# Copyright 2108-2019 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime

from odoo.addons.stock_barcodes_gs1.tests.test_stock_barcodes_gs1 import (
    TestStockBarcodesGS1,
)


class TestStockBarcodesGS1Expiry(TestStockBarcodesGS1):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Barcode with expiry data
        cls.gs1_barcode_01_exiry_date = "01184105252449301714070410AB-123"
        cls.gs1_barcode_01_use_date = "01184105252449301519070410AB-123"

    def test_wizard_scan_prueba(self):
        # Create a packaging for product
        self.product_wo_tracking_gs1.tracking = "lot"
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
                            "clean_after_done": False,
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
            }
        )
        self.action_barcode_scanned(wiz_inventory, self.gs1_barcode_01_exiry_date)
        self.action_barcode_scanned(wiz_inventory, self.gs1_barcode_01_use_date)
        wiz_inventory.action_confirm()
        self.assertEqual(
            wiz_inventory.lot_id.expiration_date, datetime(2014, 7, 4, 0, 0)
        )
        self.assertEqual(wiz_inventory.lot_id.use_date, datetime(2019, 7, 4, 0, 0))
