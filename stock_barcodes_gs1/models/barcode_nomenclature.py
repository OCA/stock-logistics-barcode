from odoo import models


class BarcodeNomenclature(models.Model):
    _inherit = "barcode.nomenclature"

    def parse_gs1_rule_pattern(self, match, rule):
        # Allow use weight ai as units directly for products with unit category uom
        result = super().parse_gs1_rule_pattern(match, rule)
        result["use_weight_as_unit"] = True if rule.use_weight_as_unit else False
        return result
