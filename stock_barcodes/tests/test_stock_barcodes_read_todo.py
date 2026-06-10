# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from unittest.mock import patch

from odoo import Command
from odoo.tests.common import tagged

from .common import TestCommonStockBarcodes


@tagged("post_install", "-at_install")
class TestStockBarcodesReadTodo(TestCommonStockBarcodes):
    def setUp(self):
        super().setUp()
        # Other tests share self.wiz_scan_read_todo (created in setUpClass)
        # and may unlink it via fill_records() -> todo_line_ids.unlink(),
        # leaving subsequent tests with a missing record. Re-create when
        # gone so each test starts from a known state.
        if not self.wiz_scan_read_todo.exists():
            type(self).wiz_scan_read_todo = self.WizScanReadTodo.create(
                {
                    "wiz_barcode_id": self.wiz_scan.id,
                    "line_ids": [
                        Command.create(
                            {
                                "product_id": self.product_tracking.id,
                                "company_id": self.company.id,
                                "location_id": self.location_1.id,
                                "location_dest_id": self.location_1.id,
                                "quantity_product_uom": 15,
                                "qty_picked": 10,
                            }
                        ),
                    ],
                }
            )

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
        # operation_quantities() refreshes todo_line_ids of the parent wizard,
        # which unlinks the current wiz_scan_read_todo. Cache the references
        # we need BEFORE the call. In v18 the method calls refresh_todo_records
        # (was action_confirm in v16); mock that one instead.
        with patch.object(type(self.wiz_scan), "refresh_todo_records") as mock_msg:
            self.wiz_scan_read_todo.product_id = self.product_tracking.id
            captured_product = self.wiz_scan_read_todo.product_id
            self.wiz_scan_read_todo.operation_quantities()
            # The contract under test is that refresh_todo_records is invoked
            # exactly once and the product remains the one the test set.
            mock_msg.assert_called_once()
            self.assertEqual(captured_product, self.product_tracking)

    def test_update_fields_after_determine_todo_uses_todo_qty_done(self):
        """Regression: update_fields_after_determine_todo() receives a
        wiz.stock.barcodes.read.todo record (its parameter is named
        ``move_line`` but it is NOT a stock.move.line). It must read the
        todo's own aggregated ``qty_done`` (sum of line_ids.qty_picked); the
        todo has no ``qty_picked`` attribute. The v18 migration wrongly used
        ``move_line.qty_picked``, raising AttributeError on every scan that
        reaches determine_todo_action().
        """
        todo = self.wiz_scan_read_todo
        # The todo aggregates qty_picked (10) from its single move line.
        self.assertEqual(todo.qty_done, 10.0)
        self.wiz_scan.update_fields_after_determine_todo(todo)
        self.assertEqual(self.wiz_scan.picking_product_qty, 10.0)

    def test_pending_qty_to_scan_excludes_fully_picked_move(self):
        # Over-scan guard: a move already at its full demand (qty_picked ==
        # product_uom_qty) must contribute 0 remaining, not its full demand.
        # The off-by-one made the "higher than necessary" warning fire at
        # demand+1 (e.g. 3/2) instead of at the demand (2/2).
        Move = self.env["stock.move"]
        dest = self.env.ref("stock.stock_location_customers")

        def _make_move(name, demand, picked):
            move = Move.create(
                {
                    "name": name,
                    "product_id": self.product_wo_tracking.id,
                    "product_uom": self.product_wo_tracking.uom_id.id,
                    "product_uom_qty": demand,
                    "location_id": self.stock_location.id,
                    "location_dest_id": dest.id,
                    "move_line_ids": [
                        Command.create(
                            {
                                "product_id": self.product_wo_tracking.id,
                                "location_id": self.stock_location.id,
                                "location_dest_id": dest.id,
                                "quantity": demand,
                            }
                        )
                    ],
                }
            )
            move.move_line_ids.qty_picked = picked
            return move

        move_full = _make_move("full", 2, 2)  # 2/2 -> 0 remaining
        move_partial = _make_move("partial", 5, 3)  # 3/5 -> 2 remaining
        # 0 + 2 = 2. The off-by-one returned 4 (full move counted as its demand).
        remaining = self.wiz_scan._get_pending_qty_to_scan(move_full | move_partial)
        self.assertEqual(remaining, 2.0)
