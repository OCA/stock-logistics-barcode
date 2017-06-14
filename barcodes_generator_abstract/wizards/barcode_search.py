# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class BarcodeSearch(models.TransientModel):
    _name = 'barcode.search'

    nomenclature_id = fields.Many2one(
        string='Nomenclature',
        comodel_name='barcode.nomenclature',
        default=lambda s: s._default_nomenclature_id(),
        required=True,
    )
    barcode = fields.Char(
        required=True,
        help='Barcode to search for.',
    )

    @api.model
    def _default_nomenclature_id(self):
        if self.env.context.get('active_model') != 'barcode.nomenclature':
            return
        return self.env.context.get('active_id')

    @api.multi
    def search(self):
        self.ensure_one()
        return self.nomenclature_id.get_form_action_for_barcode(
            self.barcode,
        )
