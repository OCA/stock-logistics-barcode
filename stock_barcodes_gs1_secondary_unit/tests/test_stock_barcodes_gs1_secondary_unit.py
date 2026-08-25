# Copyright 2108-2019 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import tagged

from odoo.addons.stock_barcodes_gs1.tests.test_stock_barcodes_gs1 import (
    TestStockBarcodesGS1,
)


@tagged("post_install", "-at_install")
class TestStockBarcodesGS1SecondaryUnit(TestStockBarcodesGS1):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.secondary_unit = cls.env["product.secondary.unit"].create(
            {
                "product_tmpl_id": cls.product_tracking.product_tmpl_id.id,
                "name": "box 8",
                "uom_id": cls.product_tracking.uom_id.id,
                "factor": 8.0,
                "barcode": "08412598033094",
            }
        )

    def test_wizard_scan_gs1_secondary_unit(self):
        # Scanning barcode with package data
        self.action_barcode_scanned(self.wiz_scan, "0108412598033094")
        self.assertEqual(self.wiz_scan.secondary_uom_id, self.secondary_unit)
        self.wiz_scan.secondary_uom_qty = 5.0
        self.wiz_scan.onchange_secondary_uom_qty()
        self.assertEqual(self.wiz_scan.product_qty, 40.0)
