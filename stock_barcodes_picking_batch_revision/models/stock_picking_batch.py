# Copyright 2023 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class StockPickingBatch(models.Model):
    _inherit = "stock.picking.batch"

    barcodes_requested_review = fields.Boolean()

    def write(self, vals):
        res = super(StockPickingBatch, self).write(vals)
        # Set not assigned batch picking to allow to be assigned to other user to review
        if vals.get("barcodes_requested_review", False):
            self.user_id = False
        return res
