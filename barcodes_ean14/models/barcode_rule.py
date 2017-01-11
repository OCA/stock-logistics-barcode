# -*- coding: utf-8 -*-
# Copyright 2016-2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class BarcodeRule(models.Model):
    _inherit = 'barcode.rule'

    encoding = fields.Selection(
        selection_add=[('ean14', 'EAN-14')],
    )
