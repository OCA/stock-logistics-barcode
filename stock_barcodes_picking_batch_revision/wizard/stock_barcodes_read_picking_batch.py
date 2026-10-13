# Copyright 2023 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class WizStockBarcodesReadPickingBatchRevision(models.TransientModel):
    _inherit = "wiz.stock.barcodes.read.picking"

    review_picking_batch = fields.Boolean(
        help="Technical field to know the context (reviewer or not)"
    )
    barcodes_requested_review = fields.Boolean(
        related="picking_batch_id.barcodes_requested_review", readonly=False
    )

    def get_moves_or_move_lines(self):
        if self.picking_mode == "picking_batch" and self.review_picking_batch:
            return self.picking_batch_id.move_line_ids
        return super().get_moves_or_move_lines()

    @api.depends(
        "review_picking_batch",
        "todo_line_ids.state",
        "todo_line_ids.line_ids.barcodes_is_reviewed",
    )
    def _compute_pending_move_ids(self):
        for wizard in self:
            if wizard.review_picking_batch:
                wizard.pending_move_ids = wizard.todo_line_ids.filtered(
                    lambda line: line.state == "pending"
                )
            else:
                super(
                    WizStockBarcodesReadPickingBatchRevision, wizard
                )._compute_pending_move_ids()
        return None

    def action_validate_picking_batch(self):
        if self.review_picking_batch and self.picking_batch_id.move_line_ids.filtered(
            lambda line: not line.barcodes_is_reviewed
        ):
            raise UserError(_("Review all operations before validating the batch."))
        return super().action_validate_picking_batch()

    def action_clean_values(self):
        """Restore review state to not reviewed"""
        if not self.review_picking_batch:
            return super().action_clean_values()
        self.picking_batch_id.move_line_ids.barcodes_is_reviewed = False
        self.fill_pending_moves()
        self.determine_todo_action()
        return True

    def action_barcodes_requested_review(self):
        self.barcodes_requested_review = not self.barcodes_requested_review
