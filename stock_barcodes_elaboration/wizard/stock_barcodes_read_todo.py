# Copyright 2023 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class WizStockBarcodesReadTodo(models.TransientModel):
    _inherit = "wiz.stock.barcodes.read.todo"

    elaboration_ids = fields.Many2many(
        comodel_name="product.elaboration",
        string="Elaborations",
        compute="_compute_elaboration_ids",
    )
    elaboration_note = fields.Char(compute="_compute_elaboration_ids")

    def _compute_elaboration_ids(self):
        for line in self:
            moves = line.stock_move_ids or line.line_ids.mapped("move_id")
            line.elaboration_ids = moves.elaboration_ids
            line.elaboration_note = ". ".join(
                m.elaboration_note for m in moves if m.elaboration_note
            )

    def _group_key(self, wiz, line):
        key = super(WizStockBarcodesReadTodo, self)._group_key(wiz, line)
        key += (line.elaboration_ids,)
        return key
