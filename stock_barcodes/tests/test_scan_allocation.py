# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests import tagged

from .test_scan_uom import ScanUomCommon


@tagged("post_install", "-at_install")
class TestScanAllocation(ScanUomCommon):
    def _sibling_picking(self, demand=2, uom=None):
        picking, _wizard = self._scan_picking(
            self.product_wo_tracking, demand, uom or self.unit
        )
        first_move = picking.move_ids
        second_move = first_move.copy(
            {
                "product_uom_qty": 1,
                "product_uom": self.unit.id,
                "move_line_ids": [],
                "state": "draft",
            }
        )
        second_move._action_confirm(merge=False)
        return picking, first_move, second_move

    def _scan_and_validate(self, picking, quantity):
        action = picking.action_barcode_scan(option_group=self.scan_options)
        wizard = self.WizScanReadPicking.browse(action["res_id"])
        wizard.manual_entry = True
        self.action_barcode_scanned(wizard, self.product_wo_tracking.barcode)
        wizard.product_qty = quantity
        wizard.action_confirm()
        wizard.action_validate_picking()
        self.assertEqual(picking.state, "done")
        self.assertEqual(
            sum(picking.move_line_ids.mapped("quantity_product_uom")), quantity
        )

    def test_allocate_unreserved_sibling_demand(self):
        picking, first_move, second_move = self._sibling_picking()
        picking.do_unreserve()
        self._scan_and_validate(picking, 3)
        self.assertEqual(first_move.quantity, 2)
        self.assertEqual(second_move.quantity, 1)

    def test_allocate_existing_line_before_unreserved_sibling(self):
        picking, first_move, second_move = self._sibling_picking()
        picking.do_unreserve()
        self.env["stock.move.line"].create(
            {
                "move_id": first_move.id,
                "picking_id": picking.id,
                "product_id": self.product_wo_tracking.id,
                "product_uom_id": self.unit.id,
                "quantity": 2,
                "location_id": picking.location_id.id,
                "location_dest_id": picking.location_dest_id.id,
            }
        )
        self._scan_and_validate(picking, 3)
        self.assertEqual(first_move.quantity, 2)
        self.assertEqual(second_move.quantity, 1)

    def test_allocate_siblings_with_different_uoms(self):
        picking, first_move, second_move = self._sibling_picking(1, self.dozen)
        picking.do_unreserve()
        self._scan_and_validate(picking, 13)
        self.assertEqual(first_move.quantity, 1)
        self.assertEqual(second_move.quantity, 1)
