# Copyright 2019 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models


class WizStockBarcodesReadPicking(models.TransientModel):
    _inherit = "wiz.stock.barcodes.read.picking"

    def _prepare_move_line_values(self, candidate_move, available_qty):
        vals = super()._prepare_move_line_values(candidate_move, available_qty)
        vals.update(
            {
                "secondary_uom_id": self.secondary_uom_id.id,
                "secondary_uom_qty": self.secondary_uom_qty,
            }
        )
        return vals

    def filter_sml(self, candidate_lines, lines, sml_vals):
        if self.secondary_uom_id:
            lines = lines.filtered(
                lambda ln: ln.secondary_uom_id == self.secondary_uom_id
                and ln.barcode_scan_state == "pending"
            )
        return lines

    def determine_todo_action(self, forced_todo_line=False):
        res = super().determine_todo_action(forced_todo_line=forced_todo_line)
        if self.option_group_id.barcode_guided_mode == "guided":
            if self.option_group_id.get_option_value(
                "secondary_uom_id", "filled_default"
            ):
                self.secondary_uom_id = self.todo_line_id.line_ids[:1].secondary_uom_id
        return res
