import barcode

from odoo import api, fields, models


class BarcodeGenerateMixin(models.AbstractModel):
    _inherit = "barcode.generate.mixin"

    def generate_barcode(self):
        for item in self:
            padding = item.barcode_rule_id.padding
            str_base = str(item.barcode_base).rjust(padding, "0")
            custom_code = self._get_custom_barcode(item)
            if custom_code:
                custom_code = custom_code.replace("." * padding, str_base)
                self._create_barcode(item, custom_code)

    @api.model
    def _create_barcode(self, item, custom_code):
        barcode_class = barcode.get_barcode_class(item.barcode_rule_id.encoding)
        self.env["product.barcode"].create(
            {
                "product_id": self.id,
                "name": barcode_class(
                    custom_code if custom_code else fields.Datetime.now().to_string()
                ),
            }
        )
