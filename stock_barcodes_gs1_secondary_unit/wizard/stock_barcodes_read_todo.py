# Copyright 2023 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.tools import float_compare


class WizStockBarcodesReadTodo(models.TransientModel):
    _inherit = ["wiz.stock.barcodes.read.todo", "product.secondary.unit.mixin"]
    _name = "wiz.stock.barcodes.read.todo"
    _secondary_unit_fields = {
        "qty_field": "product_uom_qty",
        "uom_field": "uom_id",
    }

    def _prepare_fill_record_values(self, wiz_barcode, line, position):
        vals = super()._prepare_fill_record_values(wiz_barcode, line, position)
        vals["secondary_uom_id"] = line.secondary_uom_id.id
        if line._name == "stock.move.line":
            move = line.move_id
            # Set secondary qty when stock.move full match with stock.move.line
            if not (move.move_line_ids - line) and not float_compare(
                move.product_uom_qty,
                line.product_uom_qty,
                precision_rounding=line.product_uom_id.rounding,
            ):
                vals["secondary_uom_qty"] = move.secondary_uom_qty
        elif line._name == "stock.move":
            # Set secondary qty when stock.move all quantity is available
            if not float_compare(
                line.reserved_availability,
                line.product_uom_qty,
                precision_rounding=line.product_uom.rounding,
            ):
                vals["secondary_uom_qty"] = line.secondary_uom_qty
        return vals

    @api.model
    def fields_to_fill_from_pending_line(self):
        res = super().fields_to_fill_from_pending_line()
        res.append("secondary_uom_id")
        return res

    def _group_key(self, wiz, line):
        key = super()._group_key(wiz, line)
        key += (line.secondary_uom_id,)
        return key
