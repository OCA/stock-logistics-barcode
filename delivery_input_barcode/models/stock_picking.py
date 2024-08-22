# copyright 2022 David BEAL @ Akretion
# copyright 2024 David Palanca @ Grupo Isonor

from odoo import models


class StockMoveLine(models.Model):
    _name = "stock.move"
    _inherit = ["stock.move", "product.barcode.line.mixin"]


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def action_move_barcode(self, barcode):
        """Create a move line according barcode information"""
        self.ensure_one()
        self.env["stock.move"].with_context(
            picking_id=self.id,
            company_id=self.company_id.id,
            location_id=self.location_id.id,
            location_dest_id=self.location_dest_id.id,
        )._process_barcode_on_product_line(barcode)
