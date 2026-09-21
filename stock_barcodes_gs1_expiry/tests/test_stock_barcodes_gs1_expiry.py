# Copyright 2108-2019 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

from odoo.fields import Command

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
        option_group = cls.env["stock.barcodes.option.group"].create(
            {
                "name": "option group for tests IN GS1",
                "create_lot": True,
                "is_manual_confirm": True,
                "option_ids": [
                    Command.create(
                        {
                            "step": 1,
                            "name": "Location",
                            "field_name": "location_id",
                            "filled_default": True,
                            "to_scan": True,
                            "required": True,
                        }
                    ),
                    Command.create(
                        {
                            "step": 2,
                            "name": "Product",
                            "field_name": "product_id",
                            "to_scan": True,
                            "required": True,
                            "clean_after_done": True,
                        }
                    ),
                    Command.create(
                        {
                            "step": 2,
                            "name": "Packaging",
                            "field_name": "packaging_id",
                            "to_scan": True,
                            "required": False,
                            "clean_after_done": True,
                        }
                    ),
                    Command.create(
                        {
                            "step": 2,
                            "name": "Lot / Serial",
                            "field_name": "lot_id",
                            "to_scan": True,
                            "required": True,
                            "clean_after_done": False,
                        }
                    ),
                ],
            }
        )
        cls.wiz_inventory = cls.env["wiz.stock.barcodes.read.inventory"].create(
            {
                "location_id": cls.env["stock.warehouse"]
                .search([])[:1]
                .lot_stock_id.id,
                "option_group_id": option_group.id,
                "step": 1,
            }
        )
        cls.date_1 = datetime(2014, 7, 4, 0, 0)
        cls.date_2 = datetime(2019, 7, 4, 0, 0)
        cls.product_remove_time = cls.env["product.template"].create(
            {"name": "Product remove time", "removal_time": 5}
        )

    def test_wizard_scan_expiry_dates(self):
        # Create a packaging for product
        self.product_wo_tracking_gs1.tracking = "lot"

        self.action_barcode_scanned(self.wiz_inventory, self.gs1_barcode_01_exiry_date)
        self.action_barcode_scanned(self.wiz_inventory, self.gs1_barcode_01_use_date)
        self.wiz_inventory.action_confirm()
        self.assertEqual(self.wiz_inventory.lot_id.expiration_date, self.date_1)
        self.assertEqual(self.wiz_inventory.lot_id.use_date, self.date_2)

    def test_prepare_lot_vals(self):
        self.product_wo_tracking_gs1.removal_time = 5
        self.product_wo_tracking_gs1.barcode = "159753624312"
        self.wiz_inventory.expiration_date = self.date_1
        self.wiz_inventory.product_id = self.product_wo_tracking_gs1.id
        result = self.wiz_inventory._prepare_lot_vals()
        self.assertEqual(
            result["removal_date"],
            self.date_1 - timedelta(days=self.product_wo_tracking_gs1.removal_time),
        )
