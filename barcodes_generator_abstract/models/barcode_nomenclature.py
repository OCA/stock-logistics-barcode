# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class BarcodeNomenclature(models.Model):
    _inherit = 'barcode.nomenclature'

    @api.multi
    def find_by_barcode(self, barcode):
        """ It returns the record associated with the barcode. """
        self.ensure_one()
        result = self.parse_barcode(barcode)
        if not result:
            return None
        barcode_rule = self.rule_ids.filtered(
            lambda r: r.type == result['type'],
        )
        if not barcode_rule.generate_model:
            return None
        return self.env[barcode_rule.generate_model].search([
            ('barcode', '=', barcode),
        ])
