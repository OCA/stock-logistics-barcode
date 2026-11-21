# Copyright 2023 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class WizStockBarcodesReadTodo(models.TransientModel):
    _inherit = "wiz.stock.barcodes.read.todo"

    elaboration_ids = fields.Many2many(
        comodel_name="product.elaboration",
        string="Elaborations",
    )
    elaboration_note = fields.Char()
