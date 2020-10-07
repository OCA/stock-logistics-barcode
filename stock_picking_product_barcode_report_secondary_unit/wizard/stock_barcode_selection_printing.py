# Copyright 2021 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from math import ceil

from odoo import api, models


class WizStockBarcodeSelectionPrinting(models.TransientModel):
    _inherit = "stock.picking.print"

    @api.model
    def _prepare_data_from_move_line(self, move_line):
        res = super()._prepare_data_from_move_line(move_line)
        if move_line.product_id.secondary_uom_ids:
            minimal_factor_sec_unit = min(
                move_line.product_id.secondary_uom_ids, key=lambda u: u.factor
            )
            res["label_qty"] = ceil(move_line.qty_done / minimal_factor_sec_unit.factor)
        return res
