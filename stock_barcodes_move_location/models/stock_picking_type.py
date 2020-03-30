# Copyright 2019 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    no_move_proposal = fields.Boolean(
        string="Do Not Propose Moves (Move On Hand)",
        help="Mark this option to not to propose stock moves to be processed",
    )
