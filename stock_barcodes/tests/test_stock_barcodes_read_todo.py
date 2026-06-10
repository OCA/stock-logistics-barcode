# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from unittest.mock import patch

from odoo.tests.common import tagged

from .common import TestCommonStockBarcodes


@tagged("post_install", "-at_install")
class TestStockBarcodesReadTodo(TestCommonStockBarcodes):
    def test_action_reset_lines(self):
        with (
            patch.object(type(self.wiz_scan), "action_clean_values"),
            patch.object(type(self.wiz_scan), "fill_todo_records"),
            patch.object(type(self.wiz_scan), "determine_todo_action") as mock_msg,
        ):
            self.wiz_scan_read_todo.action_reset_lines()
            self.wiz_scan_read_todo.line_ids._compute_barcode_scan_state()
            self.assertEqual(self.wiz_scan_read_todo.state, "pending")
            self.assertEqual(self.wiz_scan_read_todo.line_ids.qty_picked, 0)
            mock_msg.assert_called_once_with()

    def test_action_reset_lines_survives_todo_unlink(self):
        # Regression: fill_todo_records() rebuilds the todo list and unlinks
        # THIS record. action_reset_lines must capture the parent wizard first
        # and not dereference self afterwards; otherwise self.wiz_barcode_id
        # raises MissingError and the whole reset rolls back (qty_picked stays).
        # The previous test mocks fill_todo_records to a no-op, so it never
        # exercised the unlink; here the mock unlinks self like the real one.
        todo = self.wiz_scan_read_todo

        def _unlink_self(*args, **kwargs):
            todo.unlink()

        with (
            patch.object(type(self.wiz_scan), "action_clean_values"),
            patch.object(
                type(self.wiz_scan), "fill_todo_records", side_effect=_unlink_self
            ),
            patch.object(type(self.wiz_scan), "determine_todo_action") as mock_det,
        ):
            # Buggy code raised MissingError here; the fix reaches the parent
            # call through the captured reference.
            todo.action_reset_lines()
            mock_det.assert_called_once_with()
        self.assertFalse(todo.exists())

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
        # operation_quantities distributes the pending quantity over the lines and
        # refreshes the todo records of the related barcode wizard.
        with patch.object(type(self.wiz_scan), "refresh_todo_records") as mock_msg:
            self.wiz_scan_read_todo.operation_quantities()
            mock_msg.assert_called_once()

    def test_manual_entry_on_edit(self):
        # Editing a pending line enables manual entry on the wizard when the
        # option group has manual_entry_on_edit set.
        self.wiz_scan.option_group_id.manual_entry_on_edit = True
        self.wiz_scan_read_todo.with_context(
            wiz_barcode_id=self.wiz_scan.id
        ).action_barcode_inventory_quant_edit()
        self.assertTrue(self.wiz_scan.manual_entry)
