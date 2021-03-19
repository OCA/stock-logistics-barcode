# Copyright 2021 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    barcode = fields.Char(string="Barcode", index=True)

    def _action_done(self):
        Quant = self.env["stock.quant"]
        normal_move_lines = self.browse()
        for ml in self:
            if ml.location_dest_id.usage == "internal":
                if ml.location_id.usage == "supplier" and ml.barcode:
                    super(
                        StockMoveLine, ml.with_context(force_barcode=ml.barcode)
                    )._action_done()
                elif ml.location_id.usage == "internal":
                    quant = Quant._gather(
                        ml.product_id,
                        ml.location_id,
                        lot_id=ml.lot_id,
                        package_id=ml.package_id,
                        owner_id=ml.owner_id,
                        strict=True,
                    )
                    super(
                        StockMoveLine, ml.with_context(force_barcode=quant.barcode)
                    )._action_done()
                else:
                    normal_move_lines |= ml
            else:
                normal_move_lines |= ml
        return super(StockMoveLine, normal_move_lines)._action_done()
