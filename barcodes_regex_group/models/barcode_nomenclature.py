# -*- coding: utf-8 -*-
# Copyright 2020 Sunflower IT
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import re
from typing import Match

from odoo import models


class BarcodeNomenclature(models.Model):
    _inherit = 'barcode.nomenclature'

    def match_pattern(self, barcode, pattern):
        match = super(BarcodeNomenclature, self).match_pattern(
            barcode, pattern)

        # We cannot use numerical content and matching groups at the same time
        numerical_content = re.search("[{][N]*[D]*[}]", pattern)
        if numerical_content:
            return match

        # If there are no regex groups in pattern, use normal matching
        has_regex_groups = re.search("[(].*[)]", pattern)
        if not has_regex_groups:
            return match

        # Perform pattern matching using 'search' instead of 'match'
        # And don't truncate barcode on search pattern length
        match['match'] = re.search(pattern, match['base_code'])

        # Abuse 'value' to store the result, since it goes to 'parsed_result'
        if match['match'] and self.env.context.get('barcodes_regex_groups'):
            match['value'] = match['match']
        return match

    def parse_barcode(self, barcode):
        model = self.env.cache['_barcode_active_model']
        this = self.with_context(barcodes_regex_groups=True)

        # filter rules by their applicability to the currently active model
        if model:
            rule_ids_filtered = this.rule_ids.filtered(
                lambda r: (not r.model_ids)
                or model in r.model_ids.mapped('model')).ids
            rule_ids_backup = this._cache['rule_ids']
            this._cache['rule_ids'] = rule_ids_filtered
            print rule_ids_filtered

        parsed_result = super(BarcodeNomenclature, this).parse_barcode(barcode)

        # restore rule_ids
        if model:
            this._cache['rule_ids'] = rule_ids_backup

        # Post-process any result of group-matching
        if isinstance(parsed_result['value'], Match):
            match = parsed_result['value']
            parsed_result['value'] = 0
            parsed_result['code'] = match.group(1)

        return parsed_result
