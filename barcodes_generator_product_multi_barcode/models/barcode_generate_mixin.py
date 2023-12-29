import barcode

from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def generate_barcode(self):
        """override to create a product.barcode instead"""
        for item in self:
            padding = item.barcode_rule_id.padding
            str_base = str(item.barcode_base).rjust(padding, "0")
            custom_code = self._get_custom_barcode(item)
            if custom_code:
                custom_code = custom_code.replace("." * padding, str_base)
                barcode_class = barcode.get_barcode_class(item.barcode_rule_id.encoding)
                self.env["product.barcode"].create(
                    {
                        "product_id": item.id,
                        "name": barcode_class(custom_code),
                    }
                )
