# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def action_open_label_type(self):
        result = super().action_open_label_type()
        default_options = self._get_print_label_default_options()
        if default_options:
            result["context"].update(default_options)
        return result

    def _get_print_label_default_options(self) -> dict:
        result = {}
        move_quantity = self.picking_type_id.print_label_option_move_quantity
        if move_quantity:
            result.update({"default_move_quantity": move_quantity})
        print_format = self.picking_type_id.print_label_option_print_format
        if print_format:
            result.update({"default_print_format": print_format})
        extra_html = self.picking_type_id.print_label_option_extra_html
        if extra_html:
            result.update({"default_extra_html": extra_html})
        pricelist = self.picking_type_id.print_label_option_pricelist_id
        if pricelist:
            result.update({"default_pricelist_id": pricelist.id})
        return result
