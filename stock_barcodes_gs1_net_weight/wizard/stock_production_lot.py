# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class WizStockBarcodesNewLot(models.TransientModel):
    _inherit = "wiz.stock.barcodes.new.lot"
    _description = "Wizard to create new lot from barcode scanner"

    weight = fields.Float(string="Net Weight",)

    def _prepare_lot_values(self):
        res = super()._prepare_lot_values()
        res.update({"weight": self.weight})
        return res

    def _decode_barcode(self, barcode):
        barcode_decoded = super()._decode_barcode(barcode)
        ai = int(3100)

        for i in range(0,6):
            weight_txt = barcode_decoded.get(str(ai+i), False)
            if weight_txt:
                # create decimal point in the numeric string before converting
                if i>0:
                    weight_txt = weight_txt[0:(5-i)]+'.'+weight_txt[(5-i):i]
                weight = float(weight_txt)
                self.weight = weight
                return barcode_decoded
        else:
            return barcode_decoded
