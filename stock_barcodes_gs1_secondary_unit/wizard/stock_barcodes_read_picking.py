# Copyright 2019 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


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
