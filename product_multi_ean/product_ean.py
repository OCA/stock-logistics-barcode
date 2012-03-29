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
from product.product import check_ean
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

    def _get_ean(self, cr, uid, ids, context=None):
        res = set()
        obj = self.pool.get('product.ean13')
        for ean in obj.browse(cr, uid, ids, context):
            res.add(ean.product_id.id)
        return list(res)

    _columns = {'ean13': fields.function(_get_main_ean13,
                                         type='many2one',
                                         obj='product.ean13',
                                         method=True,
                                         string='Main EAN13',
                                         store ={'product.ean13':(_get_ean, [],10)}),
                'ean13_ids': fields.one2many('product.ean13', 'product_id', 'EAN13')}

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

    _columns = {'name': fields.char('EAN13', size=13),
                'product_id': fields.many2one('product.product', 'Product'),
                'sequence': fields.integer('Sequence'),}

    _defaults = {'sequence': lambda *a: 1}

    _order = 'sequence'

    def _check_ean_key(self, cr, uid, ids):
        res = False
        for ean in self.browse(cr, uid, ids):
            res = check_ean(ean.name)
            if not res:
                return res
        return res

    _constraints = [(_check_ean_key, 'Error: Invalid ean code', ['name'])]

ProductEan13()
