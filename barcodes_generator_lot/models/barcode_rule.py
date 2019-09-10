# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class BarcodeRule(models.Model):
    _inherit = 'barcode.rule'

    generate_model = fields.Selection(
        selection_add=[('stock.production.lot', 'Stock Production Lot')],
    )

    encoding = fields.Selection(
        selection_add=[('custom', 'Custom')]
    )

    @api.onchange('encoding')
    def _onchange_encoding(self):
        res = {}
        if self.encoding == 'custom' and self.type != 'lot':
            self.encoding = 'any'
            message = _('Custom Encoding is only available for Lot')
            res['warning'] = {'title': _('Warning'), 'message': message}

        return res
