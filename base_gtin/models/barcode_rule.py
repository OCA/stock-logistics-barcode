# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models


class BarcodeRule(models.Model):
    _inherit = 'barcode.rule'

    @api.model
    def _encoding_selection_list(self):
        res = super(BarcodeRule, self)._encoding_selection_list()
        return res + [('ean14', 'EAN-14')]
