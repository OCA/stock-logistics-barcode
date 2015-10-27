# -*- coding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Julius Network Solutions SARL <contact@julius.fr>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from openerp import api, models, fields, _
from openerp import exceptions


def isodd(x):
    return bool(x % 2)


class ProductCategory(models.Model):
    _inherit = 'product.category'

    ean_sequence_id = fields.Many2one('ir.sequence', string='Ean sequence')


class ProductProduct(models.Model):
    _inherit = 'product.product'

    ean13 = fields.Char(copy=False)
    ean_sequence_id = fields.Many2one('ir.sequence', string='Ean sequence')

    @api.model
    def _get_ean_next_code(self, product):
        sequence_obj = self.env['ir.sequence']
        if product.ean_sequence_id:
            ean = sequence_obj.next_by_id(product.ean_sequence_id.id)
        elif product.categ_id.ean_sequence_id:
            ean = sequence_obj.next_by_id(product.categ_id.ean_sequence_id.id)
        elif product.company_id and product.company_id.ean_sequence_id:
            ean = sequence_obj.next_by_id(
                product.company_id.ean_sequence_id.id)
        elif self.env.context.get('sequence_id', False):
            ean = sequence_obj.next_by_id(self.env.context.get('sequence_id'))
        else:
            return None
        ean = (len(ean[0:6]) == 6 and ean[0:6] or
               ean[0:6].ljust(6, '0')) + ean[6:].rjust(6, '0')
        if len(ean) > 12:
            raise exceptions.Warning(
                _("Configuration Error!"
                  "The next sequence is longer than 12 characters. "
                  "It is not valid for an EAN13 needing 12 characters, "
                  "the 13 being used as a control digit"
                  "You will have to redefine the sequence or create a new one")
                )

        return ean

    def _get_ean_control_digit(self, code):
        sum = 0
        for i in range(12):
            if isodd(i):
                sum += 3 * int(code[i])
            else:
                sum += int(code[i])
        key = (10 - sum % 10) % 10
        return '%d' % key

    @api.model
    def _generate_ean13_value(self, product):
        ean = self._get_ean_next_code(product)
        if not ean:
            return None
        key = self._get_ean_control_digit(ean)
        ean13 = ean + key
        return ean13

    @api.one
    def generate_ean13(self):
        if not self.ean13:
            ean13 = self._generate_ean13_value(self)
            if ean13:
                self.write({'ean13': ean13})

        return True
