# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models, _
from odoo.exceptions import UserError


class BarcodeNomenclature(models.Model):
    _inherit = 'barcode.nomenclature'

    @api.multi
    def find_by_barcode(self, barcode):
        """Return the record associated with the barcode.

        Args:
            barcode (str): Barcode string to search for.

        Returns:
            BaseModel: A record matching the barcode, if existing.
            None: No match.
        """
        self.ensure_one()
        result = self.parse_barcode(barcode)
        if not result:
            return None
        barcode_rules = self.rule_ids.filtered(
            lambda r: r.type == result['type'],
        )
        for barcode_rule in barcode_rules:
            if not barcode_rule.generate_model:
                continue
            record = self.env[barcode_rule.generate_model].search([
                ('barcode', '=', barcode),
            ])
            if record:
                return record

    @api.multi
    def get_form_action_for_barcode(self, barcode):
        """Return the form action for the record related to barcode.

        Args:
            barcode (str): Barcode string to search for.

        Returns:
            dict: Default form action dictionary for the barcode.

        Raises:
            UserError: If no match was found for the barcode.
        """
        barcode_record = self.find_by_barcode(barcode)
        if not barcode_record:
            raise UserError(
                _('Cannot find a record matching the barcode "%s".') % (
                    barcode,
                ),
            )
        return barcode_record.get_formview_action()
