# Copyright 2108-2019 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from unittest.mock import patch

from odoo import Command
from odoo.tests.common import tagged

from .common import TestCommonStockBarcodes


@tagged("post_install", "-at_install")
class TestStockMove(TestCommonStockBarcodes):
    def test_action_barcode_detailed_operation_unlink(self):
        self.env = self.env(
            context=dict(self.env.context, wiz_barcode_id=self.wiz_scan.id)
        )
        with (
            patch.object(type(self.StockMove), "_action_assign") as mock_action_assign,
            patch.object(
                type(self.WizScanReadPicking), "fill_todo_records"
            ) as mock_fill_todo,
            patch.object(
                type(self.WizScanReadPicking), "determine_todo_action"
            ) as mock_determine_todo_action,
        ):
            self.stock_move_test.move_line_ids[
                0
            ].action_barcode_detailed_operation_unlink()
            mock_action_assign.assert_called_once()
            mock_fill_todo.assert_called_once()
            mock_determine_todo_action.assert_called_once()
            self.assertEqual(self.stock_move_test.barcode_backorder_action, "pending")
            with self.assertRaises(ValueError):
                self.stock_move_test.move_line_ids.ensure_one()

    def test_barcode_scan_state(self):
        line = self.stock_move_test.move_line_ids[0]
        line.quantity = 5
        line._compute_barcode_scan_state()
        self.assertEqual(line.barcode_scan_state, "pending")
        line.qty_picked = 15
        line._compute_barcode_scan_state()
        self.assertEqual(line.barcode_scan_state, "done")

    def test_barcode_scan_state_zero_demand(self):
        # A line with no demand and nothing picked must NOT be flagged done
        # (0 >= 0 used to evaluate as done, leaving phantom 0/0 "done" lines).
        line = self.stock_move_test.move_line_ids[0]
        line.quantity = 0
        line.qty_picked = 0
        line._compute_barcode_scan_state()
        self.assertEqual(line.barcode_scan_state, "pending")

    def test_barcode_scan_state_keeps_done_forced(self):
        # A line forced by scanning keeps its done_forced state and is not
        # downgraded to plain "done" by the recompute.
        line = self.stock_move_test.move_line_ids[0]
        line.quantity = 0
        line.qty_picked = 5
        line.barcode_scan_state = "done_forced"
        line._compute_barcode_scan_state()
        self.assertEqual(line.barcode_scan_state, "done_forced")

    def test_barcode_action_assign_unpicks_moves_without_picked_lines(self):
        # Removing the scanned lines of a picked move must allow to reserve it
        # again: _action_assign skips picked moves.
        product = self.product_wo_tracking
        destination = self.env.ref("stock.stock_location_customers")
        self.StockQuant._update_available_quantity(product, self.location_1, 5)
        picking = self.StockPicking.create(
            {
                "picking_type_id": self.env.ref("stock.picking_type_out").id,
                "location_id": self.location_1.id,
                "location_dest_id": destination.id,
                "move_ids": [
                    Command.create(
                        {
                            "product_id": product.id,
                            "product_uom": product.uom_id.id,
                            "product_uom_qty": 5,
                            "location_id": self.location_1.id,
                            "location_dest_id": destination.id,
                        }
                    )
                ],
            }
        )
        picking.action_confirm()
        picking.action_assign()
        move = picking.move_ids
        move.move_line_ids.picked = True
        move.move_line_ids.unlink()
        self.assertTrue(move.picked)
        move._barcode_action_assign()
        self.assertFalse(move.picked)
        self.assertEqual(move.quantity, 5)
