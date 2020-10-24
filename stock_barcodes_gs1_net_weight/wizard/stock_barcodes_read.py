
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class WizStockBarcodesRead(models.AbstractModel):
    _inherit = "wiz.stock.barcodes.read"

    weight = fields.Float(string="Net Weight",)

    def _prepare_lot_values(self, barcode_decoded):
        res = super()._prepare_lot_values(barcode_decoded)
        ai = int(3100)

        for i in range(0,6):
            weight_txt = barcode_decoded.get(str(ai+i), False)
            if weight_txt:
                # create decimal point in the numeric string before converting
                if i>0:
                    weight_txt = weight_txt[0:(5-i)]+'.'+weight_txt[(5-i):i]
                weight = float(weight_txt)
                res["weight"] = weight
                return res
        else:
            return res
