# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'
    default_barcode_type = fields.Selection(
        lambda s: s.env['barcode.rule']._get_type_selection(),
        default='any',
    )
