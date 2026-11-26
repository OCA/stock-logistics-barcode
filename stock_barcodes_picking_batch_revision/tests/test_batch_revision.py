# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import Command
from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestBatchRevision(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {"name": "Review product", "is_storable": True, "barcode": "REVIEW-01"}
        )
        cls.location = cls.env.ref("stock.stock_location_stock")
        cls.destination = cls.env.ref("stock.stock_location_customers")
        cls.picking_type = cls.env.ref("stock.picking_type_out")
        cls.options = cls.env.ref(
            "stock_barcodes.stock_barcodes_option_group_operation"
        ).copy(
            {
                "name": "Review options",
                "manual_entry": True,
                "is_manual_qty": True,
                "is_manual_confirm": True,
                "barcode_guided_mode": False,
                "source_pending_moves": "move_ids",
            }
        )
        cls.picking_type.barcode_option_group_id = cls.options
        cls.env["stock.quant"].create(
            {
                "product_id": cls.product.id,
                "location_id": cls.location.id,
                "quantity": 20,
            }
        )

    def _create_scanned_batch(self):
        pickings = self.env["stock.picking"]
        for quantity in (2, 3):
            pickings |= self.env["stock.picking"].create(
                {
                    "picking_type_id": self.picking_type.id,
                    "location_id": self.location.id,
                    "location_dest_id": self.destination.id,
                    "move_ids": [
                        Command.create(
                            {
                                "name": self.product.name,
                                "product_id": self.product.id,
                                "product_uom": self.product.uom_id.id,
                                "product_uom_qty": quantity,
                                "location_id": self.location.id,
                                "location_dest_id": self.destination.id,
                            }
                        )
                    ],
                }
            )
        pickings.action_confirm()
        pickings.action_assign()
        batch = self.env["stock.picking.batch"].create(
            {"picking_ids": [Command.set(pickings.ids)]}
        )
        batch.action_confirm()
        action = batch.action_barcode_scan()
        wizard = self.env["wiz.stock.barcodes.read.picking"].browse(action["res_id"])
        wizard.location_id = self.location
        wizard.location_dest_id = self.destination
        wizard._barcode_scanned = self.product.barcode
        wizard._on_barcode_scanned()
        wizard.dummy_on_barcode_scanned()
        wizard.product_qty = 5
        wizard.action_confirm()
        self.assertEqual(sum(batch.move_line_ids.mapped("qty_picked")), 5)
        return batch

    def _review_batch(self, display_mode):
        self.options.show_pending_moves = display_mode
        batch = self._create_scanned_batch()
        action = batch.with_context(
            default_review_picking_batch=True
        ).action_barcode_scan()
        wizard = self.env["wiz.stock.barcodes.read.picking"].browse(action["res_id"])
        self.assertTrue(wizard.review_picking_batch)
        self.assertEqual(wizard.todo_line_ids.line_ids, batch.move_line_ids)
        self.assertTrue(wizard.pending_move_ids)
        with self.assertRaises(UserError):
            wizard.action_validate_picking_batch()
        for card in wizard.todo_line_ids:
            card.action_confirm_review()
        self.assertFalse(wizard.pending_move_ids)
        wizard.action_clean_values()
        self.assertFalse(any(batch.move_line_ids.mapped("barcodes_is_reviewed")))
        self.assertTrue(
            wizard.todo_line_ids.filtered(lambda card: card.state == "pending"),
        )
        self.assertTrue(wizard.pending_move_ids)
        for card in wizard.todo_line_ids:
            card.action_confirm_review()
        self.assertFalse(wizard.pending_move_ids)
        wizard.action_validate_picking_batch()
        self.assertEqual(batch.state, "done")
        self.assertEqual(sorted(batch.picking_ids.mapped("state")), ["done", "done"])
        self.assertEqual(sorted(batch.move_ids.mapped("quantity")), [2, 3])

    def test_review_with_all_moves_displayed(self):
        self._review_batch("all")

    def test_review_with_pending_moves_displayed(self):
        self._review_batch("pending")

    def test_review_with_moves_hidden(self):
        self._review_batch("none")
