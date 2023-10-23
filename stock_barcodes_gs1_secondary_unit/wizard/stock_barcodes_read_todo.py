# Copyright 2023 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class WizStockBarcodesReadTodo(models.TransientModel):
    _inherit = "wiz.stock.barcodes.read.todo"

    secondary_uom_qty = fields.Float(
        string="Secondary Qty",
        digits="Product Unit of Measure",
        readonly=True,
    )
    secondary_uom_id = fields.Many2one(
        comodel_name="product.secondary.unit",
        string="Second unit",
        readonly=True,
    )

    def _prepare_fill_record_values(self, wiz_barcode, line, position):
        vals = super()._prepare_fill_record_values(wiz_barcode, line, position)
        vals.update(
            {
                "secondary_uom_qty": line.secondary_uom_qty,
                "secondary_uom_id": line.secondary_uom_id.id,
            }
        )
        return vals

    def _update_fill_record_values(self, wiz_barcode, line, vals):
        vals = super()._update_fill_record_values(wiz_barcode, line, vals)
        vals["secondary_uom_qty"] += line.secondary_uom_qty
        return vals

    @api.model
    def fields_to_fill_from_pending_line(self):
        res = super().fields_to_fill_from_pending_line()
        res.extend(["secondary_uom_qty", "secondary_uom_id"])
        return res

    def _group_key(self, wiz, line):
        key = super()._group_key(wiz, line)
        key += (line.secondary_uom_id,)
        return key
