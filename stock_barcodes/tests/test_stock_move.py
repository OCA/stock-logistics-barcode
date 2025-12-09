# Copyright 2108-2019 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from unittest.mock import patch

from odoo.tests.common import tagged

from .common import TestCommonStockBarcodes


@tagged("post_install", "-at_install")
class TestStockMove(TestCommonStockBarcodes):
    def test_action_barcode_detailed_operation_unlink(self):
        self.env.context = dict(self.env.context, wiz_barcode_id=self.wiz_scan.id)
        with patch.object(
            type(self.StockMove), "_action_assign"
        ) as mock_action_assign, patch.object(
            type(self.WizScanReadPicking), "fill_todo_records"
        ) as mock_fill_todo, patch.object(
            type(self.WizScanReadPicking), "determine_todo_action"
        ) as mock_determine_todo_action:
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
