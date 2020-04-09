# Copyright 2019 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class WizStockBarcodesNewLot(models.TransientModel):
    _inherit = "wiz.stock.barcodes.new.lot"
    _description = "Wizard to create new lot from barcode scanner"

    life_date = fields.Datetime(string="End of Life Date",)
    use_date = fields.Datetime(string="Best before Date",)

    def _prepare_lot_values(self):
        res = super()._prepare_lot_values()
        res.update({"use_date": self.use_date, "life_date": self.life_date})
        return res

    def _decode_barcode(self, barcode):
        barcode_decoded = super()._decode_barcode(barcode)
        preferred_date = barcode_decoded.get("15", False)
        life_date = barcode_decoded.get("17", False)
        if preferred_date:
            self.use_date = preferred_date
        if life_date:
            self.life_date = life_date
        return barcode_decoded
