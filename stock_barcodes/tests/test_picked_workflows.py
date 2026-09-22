# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests import Form, tagged

from .test_scan_uom import ScanUomCommon


@tagged("post_install", "-at_install")
class TestPickedWorkflows(ScanUomCommon):
    def _reserved_picking(self):
        self.StockQuant._update_available_quantity(
            self.product_wo_tracking, self.location_1, 10
        )
        return self._scan_picking(
            self.product_wo_tracking, 10, self.unit, incoming=False
        )

    def _validate_partial(self, picking, quantity):
        action = picking.button_validate()
        self.assertEqual(action["res_model"], "stock.backorder.confirmation")
        confirmation = Form(
            self.env[action["res_model"]].with_context(**action["context"])
        ).save()
        confirmation.process()
        self.assertEqual(picking.state, "done")
        self.assertEqual(picking.move_ids.quantity, quantity)
        self.assertEqual(picking.move_ids.qty_picked, quantity)
        backorder = self.StockPicking.search([("backorder_id", "=", picking.id)])
        self.assertEqual(backorder.move_ids.product_uom_qty, 10 - quantity)
        self.assertFalse(backorder.move_ids.picked)
        self.assertEqual(backorder.move_ids.qty_picked, 0)
        self.assertEqual(
            self.StockQuant._get_available_quantity(
                self.product_wo_tracking,
                self.env.ref("stock.stock_location_customers"),
            ),
            quantity,
        )

    def test_validate_without_using_picked_quantity(self):
        picking, _wizard = self._reserved_picking()
        self.assertEqual(picking.move_ids.quantity, 10)
        self.assertEqual(picking.move_ids.qty_picked, 0)
        self.assertFalse(picking.move_ids.picked)
        picking.button_validate()
        self.assertEqual(picking.state, "done")
        self.assertEqual(picking.move_ids.quantity, 10)
        self.assertEqual(picking.move_ids.qty_picked, 10)

    def test_manual_quantity_without_using_picked_quantity(self):
        picking, _wizard = self._reserved_picking()
        picking.move_line_ids.quantity = 3
        self.assertEqual(picking.move_ids.qty_picked, 0)
        self._validate_partial(picking, 3)

    def test_scan_then_validate_from_picking(self):
        picking, wizard = self._reserved_picking()
        for _index in range(3):
            self.action_barcode_scanned(wizard, self.product_wo_tracking.barcode)
        self.assertEqual(picking.move_ids.quantity, 10)
        self.assertEqual(picking.move_ids.qty_picked, 3)
        self._validate_partial(picking, 3)

    def test_scan_then_finish_manually(self):
        picking, wizard = self._reserved_picking()
        self.action_barcode_scanned(wizard, self.product_wo_tracking.barcode)
        picking.move_line_ids.qty_picked = 4
        self._validate_partial(picking, 4)

    def test_manual_picking_then_scan(self):
        picking, wizard = self._reserved_picking()
        picking.move_line_ids.qty_picked = 2
        self.action_barcode_scanned(wizard, self.product_wo_tracking.barcode)
        self._validate_partial(picking, 3)

    def test_unpick_clears_partial_scans(self):
        picking, wizard = self._reserved_picking()
        self.action_barcode_scanned(wizard, self.product_wo_tracking.barcode)
        picking.move_ids.picked = False
        self.assertEqual(picking.move_line_ids.qty_picked, 0)
        self.assertEqual(picking.move_ids.qty_picked, 0)
        self.assertEqual(picking.move_ids.quantity, 10)
        picking.move_line_ids.quantity = 4
        self._validate_partial(picking, 4)
