# -*- encoding: utf-8 -*-
##############################################################################
#
#    Author Guewen Baconnier. Copyright Camptocamp SA
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
##############################################################################

import product as base_product
import math
from osv import osv, fields


class ProductProduct(osv.osv):
    _inherit = 'product.product'

    def _get_main_ean13(self, cr, uid, ids, field_name, arg, context):
        values = {}
        for product in self.browse(cr, uid, ids, context):
            ean13 = False
            if product.ean13_ids:
                # get the first ean13 as main ean13
                ean13 = product.ean13_ids[0].id
            values[product.id] = ean13
        return values

    _columns = {
        'ean13': fields.function(_get_main_ean13, type='many2one',
                                 obj='product.ean13', method=True,
                                 string='Main EAN13'),
        'ean13_ids': fields.one2many('product.ean13', 'product_id', 'EAN13'),
    }

    # disable constraint
    def _check_ean_key(self, cr, uid, ids):
        "Inherit the method to disable the EAN13 check"
        return True

    _constraints = [(_check_ean_key, 'Error: Invalid ean code', ['ean13'])]

ProductProduct()


class ProductEan13(osv.osv):
    _name = 'product.ean13'
    _description = "List of EAN13 for a product."

    _columns = {
        'name': fields.char('EAN13', size=13),
        'product_id': fields.many2one('product.product', 'Product'),
        'sequence': fields.integer('Sequence'),
    }

    _defaults = {
        'sequence': lambda *a: 1,
    }

    _order = 'sequence'

    # original code taken from OpenERP code (product/product.py)
    def _check_ean_key(self, cr, uid, ids):
        def is_pair(x):
            return not x % 2

        for ean in self.browse(cr, uid, ids):
            if not ean.name:
                continue
            if len(ean.name) != 13:
                return False
            try:
                int(ean.name)
            except:
                return False
            sum = 0
            for i in range(12):
                if is_pair(i):
                    sum += int(ean.name[i])
                else:
                    sum += 3 * int(ean.name[i])
            check = int(math.ceil(sum / 10.0) * 10 - sum)
            if check != int(ean.name[12]):
                return False
        return True

    _constraints = [(_check_ean_key, 'Error: Invalid ean code', ['name'])]

ProductEan13()
