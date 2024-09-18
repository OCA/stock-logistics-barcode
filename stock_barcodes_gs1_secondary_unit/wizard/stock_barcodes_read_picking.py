# Copyright 2019 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models
from odoo.tools import float_compare


class WizStockBarcodesReadPicking(models.TransientModel):
    _inherit = "wiz.stock.barcodes.read.picking"

    # Extended from stock_barcodes_read base model
    total_secondary_uom_qty = fields.Float(compute="_compute_total_secondary_uom")
    total_secondary_uom_qty_done = fields.Float(compute="_compute_total_secondary_uom")

    @api.depends("picking_id.move_line_ids.secondary_uom_qty")
    def _compute_total_secondary_uom(self):
        self.total_secondary_uom_qty = 0.0
        self.total_secondary_uom_qty_done = 0.0
        for rec in self:
            product_moves = rec.picking_id.move_lines.filtered(
                lambda ln: ln.product_id.ids == self.product_id.ids
                and ln.state != "cancel"
            )
            for sm in product_moves:
                rec.total_secondary_uom_qty += sm.secondary_uom_qty
                rec.total_secondary_uom_qty_done += sum(
                    sm.move_line_ids.mapped("secondary_uom_qty")
                )

    def _prepare_move_line_values(self, candidate_move, available_qty):
        vals = super()._prepare_move_line_values(candidate_move, available_qty)
        vals.update(
            {
                "secondary_uom_id": self.secondary_uom_id.id,
                "secondary_uom_qty": self.secondary_uom_qty,
            }
        )
        return vals

    def _get_candidate_line_domain(self):
        domain = super(WizStockBarcodesReadPicking, self)._get_candidate_line_domain()
        if self.secondary_uom_id:
            domain.extend(
                [
                    ("secondary_uom_id", "=", self.secondary_uom_id.id),
                ]
            )
        return domain

    def _update_stock_move_line(self, line, sml_vals):
        if self.secondary_uom_id:
            sml_vals["secondary_uom_qty"] = (
                line.secondary_uom_qty + self.secondary_uom_qty
            )
        return super()._update_stock_move_line(line, sml_vals)

    def _prepare_fill_record_values(self, line, position):
        vals = super()._prepare_fill_record_values(line, position)
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

    def _group_key(self, line):
        key = super()._group_key(line)
        if not self.option_group_id.group_key_for_todo_records:
            key += (line.secondary_uom_id.id,)
        return key
