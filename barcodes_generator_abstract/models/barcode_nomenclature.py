# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models, _
from odoo.exceptions import UserError


class BarcodeNomenclature(models.Model):
    _inherit = 'barcode.nomenclature'

    @api.multi
    def find_by_barcode(self, barcode):
        """ Return the record associated with the barcode. """
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

    @api.multi
    def get_form_action_for_barcode(self, barcode):
        """ Return the form action for the record related to barcode. """
        self.ensure_one()
        barcode = self.find_by_barcode(barcode)
        if not barcode:
            raise UserError(
                _('Cannot find a record matching the barcode "%s".') % (
                    barcode,
                ),
            )
        return barcode.get_formview_action()
