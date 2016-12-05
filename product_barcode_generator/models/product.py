# -*- coding: utf-8 -*-
###############################################################################
#
#    odoo, Open Source Management Solution
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

from odoo import api, models, fields, _
from odoo import exceptions


def isodd(x):
    return bool(x % 2)


class ProductCategory(models.Model):
    _inherit = 'product.category'

    barcode_sequence_id = fields.Many2one(comodel_name='ir.sequence',
                                          string='Ean sequence')


class ProductProduct(models.Model):
    _inherit = 'product.template'

    @api.one
    def generate_barcode(self):
        return self.product_variant_ids.generate_barcode()


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def _get_barcode_next_code(self, ):
        if self.categ_id.barcode_sequence_id:
            barcode = self.categ_id.barcode_sequence_id.next_by_id()
        elif self.company_id and self.company_id.barcode_sequence_id:
            barcode = self.company_id.barcode_sequence_id.next_by_id()
        else:
            barcode = self.env['ir.sequence'].\
                next_by_code('product.barcode.code')

        barcode = (len(barcode[0:6]) == 6 and barcode[0:6] or
                   barcode[0:6].ljust(6, '0')) + barcode[6:].rjust(6, '0')
        if len(barcode) > 12:
            raise exceptions.Warning(
                _("Configuration Error!"
                  "The next sequence is longer than 12 characters. "
                  "It is not valid for an EAN13 needing 12 characters, "
                  "the 13 being used as a control digit"
                  "You will have to redefine the sequence or create a new one")
            )

        return barcode

    def _get_barcode_control_digit(self, barcode):
        sum = 0
        for i in range(12):
            if isodd(i):
                sum += 3 * int(barcode[i])
            else:
                sum += int(barcode[i])
        key = (10 - sum % 10) % 10
        return '%d' % key

    @api.model
    def _generate_barcode_value(self):
        barcode = self._get_barcode_next_code()
        if not barcode:
            return None
        return barcode + self._get_barcode_control_digit(barcode)

    @api.one
    def generate_barcode(self):
        if self.barcode:
            return
        barcode = self._generate_barcode_value()
        if not barcode:
            return
        self.write({'barcode': barcode})
        return True
