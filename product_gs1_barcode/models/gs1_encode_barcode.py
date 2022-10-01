from odoo import models


class ProductProduct(models.Model):
    _name = "product.product"
    _inherit = ["product.product", "gs1.encode.barcode"]

    def _encode_gs1_vals(self):
        result = super()._encode_gs1_vals()
        result.update({"01": self.barcode})
        return result


class StockProductionLot(models.Model):
    _name = "stock.production.lot"
    _inherit = ["stock.production.lot", "gs1.encode.barcode"]

    def _encode_gs1_vals(self):
        result = self.product_id._encode_gs1_vals()
        result.update(super(StockProductionLot, self)._encode_gs1_vals())
        result.update({"10": self.name})
        if "expiration_date" in self._fields and self.expiration_date:
            # This way, we can avoid a glue module for product_expiry
            result["17"] = self.expiration_date
        return result
