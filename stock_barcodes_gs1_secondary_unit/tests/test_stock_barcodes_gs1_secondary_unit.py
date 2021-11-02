# Copyright 2108-2019 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import tagged

from odoo.addons.stock_barcodes.tests.test_stock_barcodes_picking import (
    TestStockBarcodesPicking,
)


@tagged("post_install", "-at_install")
class TestStockBarcodesGS1SecondaryUnit(TestStockBarcodesPicking):
    def setUp(self):
        super().setUp()
        self.barcode_secondary_uom = "01195011015300011714070410AB-123"
        self.secondary_unit = self.env["product.secondary.unit"].create(
            {
                "product_tmpl_id": self.product_tracking.product_tmpl_id.id,
                "name": "box 8",
                "uom_id": self.product_tracking.uom_id.id,
                "factor": 8.0,
                "barcode": "19501101530001",
            }
        )

    def test_wizard_scan_gs1_secondary_unit(self):
        # Scanning barcode with package data
        self.action_barcode_scanned(self.wiz_scan_picking, self.barcode_secondary_uom)
        self.assertEqual(self.wiz_scan_picking.secondary_uom_id, self.secondary_unit)
        self.wiz_scan_picking.secondary_uom_qty = 5.0
        self.wiz_scan_picking.onchange_secondary_uom_qty()
        self.assertEqual(self.wiz_scan_picking.product_qty, 40.0)

    def test_picking_wizard_scan_package_secondary_uom(self):
        self.action_barcode_scanned(self.wiz_scan_picking, self.barcode_secondary_uom)
        self.assertEqual(self.wiz_scan_picking.product_qty, 8.0)
        sml = self.picking_in_01.move_line_ids.filtered(
            lambda x: x.product_id == self.product_tracking
        )
        self.assertEqual(sml.secondary_uom_id, self.wiz_scan_picking.secondary_uom_id)
