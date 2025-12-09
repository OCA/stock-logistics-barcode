# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from unittest.mock import patch

from odoo.tests.common import tagged

from .common import TestCommonStockBarcodes


@tagged("post_install", "-at_install")
class TestStockBarcodesReadTodo(TestCommonStockBarcodes):
    def test_action_reset_lines(self):
        with patch.object(type(self.wiz_scan), "action_clean_values"), patch.object(
            type(self.wiz_scan), "fill_todo_records"
        ), patch.object(type(self.wiz_scan), "determine_todo_action") as mock_msg:
            self.wiz_scan_read_todo.action_reset_lines()
            self.wiz_scan_read_todo.line_ids._compute_barcode_scan_state()
            self.assertEqual(self.wiz_scan_read_todo.state, "pending")
            self.assertEqual(self.wiz_scan_read_todo.line_ids.qty_picked, 0)
            mock_msg.assert_called_once_with()

    def test_fields_to_fill_from_pending_line(self):
        return_values = [
            "location_id",
            "location_dest_id",
            "product_id",
            "lot_id",
            "package_id",
        ]
        self.wiz_scan_read_todo.wiz_barcode_id.keep_result_package = True
        result = self.wiz_scan_read_todo.fields_to_fill_from_pending_line()
        self.assertEqual(result, return_values)

        return_values.append("result_package_id")
        self.wiz_scan_read_todo.wiz_barcode_id.keep_result_package = False
        result = self.wiz_scan_read_todo.fields_to_fill_from_pending_line()
        self.assertEqual(result, return_values)

    def test_operation_quantities(self):
        with patch.object(type(self.wiz_scan), "action_confirm") as mock_msg:
            self.wiz_scan_read_todo.product_id = self.product_tracking.id
            self.wiz_scan_read_todo.operation_quantities()
            self.assertTrue(self.wiz_scan_read_todo.wiz_barcode_id.manual_entry)
            self.assertEqual(self.wiz_scan_read_todo.product_id, self.product_tracking)
            mock_msg.assert_called_once()
