# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    print_label_option_print_format = fields.Selection(
        selection=lambda self: self._get_print_label_option_print_format(),
    )
    print_label_option_move_quantity = fields.Selection(
        selection=lambda self: self._get_print_label_option_move_quantity(),
    )
    print_label_option_extra_html = fields.Html()
    print_label_option_pricelist_id = fields.Many2one(
        comodel_name="product.pricelist",
    )

    @api.model
    def _get_print_label_option_print_format(self):
        selections = (
            self.env["product.label.layout"]
            ._fields.get("print_format")
            ._description_selection(self.env)
        )
        return selections

    @api.model
    def _get_print_label_option_move_quantity(self):
        selections = (
            self.env["product.label.layout"]
            ._fields.get("move_quantity")
            ._description_selection(self.env)
        )
        return selections
