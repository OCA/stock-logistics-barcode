# Copyright 2023 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class WizStockBarcodesReadPickingBatchRevision(models.TransientModel):
    _inherit = "wiz.stock.barcodes.read.picking"

    review_picking_batch = fields.Boolean(
        help="Technical field to know the context (reviewer or not)"
    )

    def _get_stock_move_lines_todo(self):
        if self.picking_mode != "picking_batch" or not self.review_picking_batch:
            return super()._get_stock_move_lines_todo()
        # Get all sml to be reviewed although it has not qty_done
        move_lines = self.picking_batch_id.move_line_ids.filtered(
            lambda ml: not ml.barcodes_is_reviewed
        )
        return move_lines

    def action_clean_values(self):
        """Restore review state to not reviewed"""
        if not self.review_picking_batch:
            return super().action_clean_values()
        self.picking_batch_id.move_line_ids.barcodes_is_reviewed = False


class WizCandidatePickingBatch(models.TransientModel):
    _inherit = "wiz.candidate.picking.batch"

    barcodes_requested_review = fields.Boolean(
        related="picking_batch_id.barcodes_requested_review", readonly=False
    )
