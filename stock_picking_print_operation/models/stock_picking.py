# Copyright 2026 ACSONE SA/NV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo import models

from odoo.addons.stock.models.stock_move import StockMove
from odoo.addons.stock.models.stock_move_line import StockMoveLine


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _get_context_values_for_print_line(self, lines: StockMoveLine):
        """
        Change default context in order to force the move lines
        to be printed
        """
        return {
            "default_product_ids": lines.product_id.ids,
            "default_move_ids": lines.move_id.ids,
            "default_move_line_ids": lines.ids,
            "default_move_quantity": "line",
        }

    def _get_context_values_for_print_move(self, moves: StockMove):
        """
        Change default context in order to force the moves
        to be printed
        """
        return {
            "default_product_ids": moves.product_id.ids,
            "default_move_ids": moves.ids,
            "default_move_quantity": "move",
        }

    def action_print_line_barcode(self, line_ids: list[int]):
        """
        This is intended to be called by external service
        too on picking level passing the line id as parameter.
        """
        self.ensure_one()
        action = self.action_open_label_type()
        lines = self.env["stock.move.line"].browse(line_ids)
        context_values = self._get_context_values_for_print_line(lines)
        if "context" in action:
            action["context"].update(context_values)
        else:
            action["context"] = context_values
        return action

    def action_print_move_barcode(self, move_ids: list[int]):
        """
        This is intended to be called by external service
        too on picking level passing the move id as parameter.
        """
        self.ensure_one()
        action = self.action_open_label_type()
        moves = self.env["stock.move"].browse(move_ids)
        context_values = self._get_context_values_for_print_move(moves)
        if "context" in action:
            action["context"].update(context_values)
        else:
            action["context"] = context_values
        return action
