# Copyright 2019 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models


class BarcodeNomenclature(models.Model):
    _inherit = "barcode.nomenclature"

    def parse_gs1_rule_pattern(self, match, rule):
        # Allow use weight ai as units directly for products with unit category uom
        result = super().parse_gs1_rule_pattern(match, rule)
        if result:
            result["use_weight_as_unit"] = bool(rule.use_weight_as_unit)
        return result
