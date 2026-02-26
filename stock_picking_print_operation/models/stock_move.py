# Copyright 2026 ACSONE SA/NV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    show_print_operation_button = fields.Boolean(
        related="picking_type_id.show_print_operation_button"
    )

    def action_print_barcode(self) -> dict:
        """
        This is intended to be called by external service
        too on picking level passing the move id as parameter.
        """
        return self.picking_id.action_print_move_barcode(self.ids)
