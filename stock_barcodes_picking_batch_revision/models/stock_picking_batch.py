# Copyright 2023 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class StockPickingBatch(models.Model):
    _inherit = "stock.picking.batch"

    barcodes_requested_review = fields.Boolean()

    def write(self, vals):
        # Unassign the batch so any other user can take the review, in the
        # same write instead of a second one
        if vals.get("barcodes_requested_review"):
            vals = dict(vals, user_id=False)
        return super().write(vals)
