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

    def test_wizard_scan_gs1_secondary_unit_ai37(self):
        """AI 02 (contained trade item GTIN) matching a secondary unit must
        route AI 37 (count of items) to secondary_uom_qty, not product_qty -
        e.g. counting pieces of fish sold by weight: the count on the label
        must land on the piece count, not get treated as a weight/qty.
        """
        secondary_unit_ai02 = self.env["product.secondary.unit"].create(
            {
                "product_tmpl_id": self.product_tracking.product_tmpl_id.id,
                "name": "box AI02",
                "uom_id": self.product_tracking.uom_id.id,
                "factor": 8.0,
                "barcode": "18412598033091",
            }
        )
        self.action_barcode_scanned(
            self.wiz_scan, "0218412598033091" + self.gs1_separator + "373"
        )
        self.assertEqual(self.wiz_scan.secondary_uom_id, secondary_unit_ai02)
        self.assertEqual(self.wiz_scan.secondary_uom_qty, 3.0)
        self.assertEqual(self.wiz_scan.product_qty, 24.0)

    def test_wizard_scan_gs1_secondary_unit_ai30(self):
        """AI 30 (variable count of items) shares the same routing hook as
        AI 37 in the base module (_set_gs1_product_qty) - must be covered
        the same way, not just AI 37.
        """
        secondary_unit_ai02 = self.env["product.secondary.unit"].create(
            {
                "product_tmpl_id": self.product_tracking.product_tmpl_id.id,
                "name": "box AI02",
                "uom_id": self.product_tracking.uom_id.id,
                "factor": 8.0,
                "barcode": "18412598033091",
            }
        )
        self.action_barcode_scanned(
            self.wiz_scan, "0218412598033091" + self.gs1_separator + "303"
        )
        self.assertEqual(self.wiz_scan.secondary_uom_id, secondary_unit_ai02)
        self.assertEqual(self.wiz_scan.secondary_uom_qty, 3.0)
        self.assertEqual(self.wiz_scan.product_qty, 24.0)
