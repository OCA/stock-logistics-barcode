# Copyright 2026 ACSONE SA/NV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking.type"

    show_print_operation_button = fields.Boolean(
        string="Show print button on Operations level",
        help="Check this if you want to display a button "
        "on operations level to print product labels",
    )
