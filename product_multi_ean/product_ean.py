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

import netsvc
from tools.translate import _
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


    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        """overwrite the search method in order to search
        on all ean13 codes of a product when we search an ean13"""

        if filter(lambda x: x[0] == 'ean13', args):
            # get the operator of the search
            ean_operator = filter(lambda x: x[0] == 'ean13', args)[0][1]
            #get the value of the search
            ean_value = filter(lambda x: x[0] == 'ean13', args)[0][2]
            # search the ean13
            ean_ids = self.pool.get('product.ean13').search(cr, uid, [('name', ean_operator, ean_value)])
            
            if not ean_ids: return []

            #get the other arguments of the search
            args = filter(lambda x: x[0] != 'ean13', args)
            #add the new criterion
            args += [('ean13_ids', 'in', ean_ids)]
        return super(ProductProduct, self).search(cr, uid, args, offset, limit, order, context=context, count=count)

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
        logger = netsvc.Logger()
        for ean in self.browse(cr, uid, ids):
            if not ean.name:
                continue
            if len(ean.name) != 13:
                logger.notifyChannel(_("EAN Validation"),
                                     netsvc.LOG_ERROR,
                                     _("EAN %s is not 13 char long" % (ean.name)))
                return False
            try:
                int(ean.name)
            except:
                logger.notifyChannel(_("EAN Validation"),
                                     netsvc.LOG_ERROR,
                                     _("EAN %s is contains non numeric value" % (ean.name)))
                return False
            sum = 0
            for i in range(12):
                if is_pair(i):
                    sum += int(ean.name[i])
                else:
                    sum += 3 * int(ean.name[i])
            check = int(math.ceil(sum / 10.0) * 10 - sum)
            if check != int(ean.name[12]):
                logger.notifyChannel(_("EAN Validation"),
                                     netsvc.LOG_ERROR,
                                     _("EAN %s check sum is wrong" % (ean.name)))
                return False
        return True

    _constraints = [(_check_ean_key, 'Error: Invalid ean code', ['name'])]

ProductEan13()
