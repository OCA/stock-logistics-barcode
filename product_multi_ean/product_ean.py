# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2012 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import logging

from openerp.osv import orm, fields
from openerp.addons.product import product


_logger = logging.getLogger(__name__)


class ProductEan13(orm.Model):
    _name = 'product.ean13'
    _description = "List of EAN13 for a product."
    _columns = {'name': fields.char('EAN13', size=13),
                'product_id':
                    fields.many2one('product.product',
                                    'Product',
                                    required=True),
                'sequence': fields.integer('Sequence'), }
    _order = 'sequence'

    def _check_ean_key(self, cr, uid, ids):
        res = False
        for ean in self.browse(cr, uid, ids):
            res = product.check_ean(ean.name)
            if not res:
                return res
        return res

    _constraints = [(_check_ean_key, 'Error: Invalid ean code', ['name'])]

    def create(self, cr, uid, vals, context=None):
        """Create ean13 with a sequence higher than all
        other products when it is not specified"""
        if not vals.get('sequence') and vals.get('product_id'):
            ean13_ids = self.search(
                cr, uid,
                [('product_id', '=', vals['product_id'])],
                context=context)
            ean13s = self.browse(cr, uid, ean13_ids, context=context)
            vals['sequence'] = 1
            if ean13s:
                vals['sequence'] = max([ean.sequence for ean in ean13s]) + 1
        return super(ProductEan13, self).create(cr, uid, vals, context=context)


class ProductProduct(orm.Model):
    _inherit = 'product.product'

    def _auto_init(self, cr, context=None):
        sql = ("SELECT data_type "
               "FROM information_schema.columns "
               "WHERE table_name = 'product_product' "
               "AND column_name = 'ean13' ")
        cr.execute(sql)
        column = cr.fetchone()
        if column[0] == 'character varying':
            # module was not installed, the column will be replaced by
            _logger.info('migrating the EAN13')
            cr.execute("INSERT INTO "
                       "product_ean13 (name, product_id, sequence) "
                       "SELECT p.ean13, p.id, 1 "
                       "FROM product_product p WHERE "
                       "p.ean13 IS NOT NULL ")
            # drop the field otherwise the function field will
            # not be computed
            cr.execute("ALTER TABLE product_product "
                       "DROP ean13")
        return super(ProductProduct, self)._auto_init(cr, context=context)

    def _get_main_ean13(self, cr, uid, ids, _field_name, _arg, context):
        values = {}
        for product in self.browse(cr, uid, ids, context=context):
            ean13 = False
            if product.ean13_ids:
                # get the first ean13 as main ean13
                ean13 = product.ean13_ids[0].id
            values[product.id] = ean13
        return values

    def _get_ean(self, cr, uid, ids, context=None):
        res = set()
        obj = self.pool.get('product.ean13')
        for ean in obj.browse(cr, uid, ids, context=context):
            res.add(ean.product_id.id)
        return list(res)

    def _write_ean(self, cr, uid, product_id, _name, value, _arg, context=None):
        product = self.browse(cr, uid, product_id, context=context)
        if value and not value in [ean.name for ean in product.ean13_ids]:
            self.pool.get('product.ean13').create(
                cr, uid,
                {'name': value, 'product_id': product.id},
                context=context)
        return True

    _columns = {
        'ean13_ids': fields.one2many('product.ean13', 'product_id', 'EAN13'),
        'ean13': fields.function(
            _get_main_ean13,
            fnct_inv=_write_ean,
            type='many2one',
            obj='product.ean13',
            string='Main EAN13',
            readonly=True,
            store={
                'product.product':
                    (lambda self, cr, uid, ids, c=None: ids, ['ean13_ids'], 10),
                'product.ean13':
                    (_get_ean, [], 10)})}

    # disable constraint
    def _check_ean_key(self, cr, uid, ids):
        "Inherit the method to disable the EAN13 check"
        return True
    _constraints = [(_check_ean_key, 'Error: Invalid ean code', ['ean13'])]

    def search(self, cr, uid, args, offset=0, limit=None,
               order=None, context=None, count=False):
        """overwrite the search method in order to search
        on all ean13 codes of a product when we search an ean13"""

        if filter(lambda x: x[0] == 'ean13', args):
            # get the operator of the search
            ean_operator = filter(lambda x: x[0] == 'ean13', args)[0][1]
            #get the value of the search
            ean_value = filter(lambda x: x[0] == 'ean13', args)[0][2]
            # search the ean13
            ean_ids = self.pool.get('product.ean13').search(
                cr, uid, [('name', ean_operator, ean_value)])

            #get the other arguments of the search
            args = filter(lambda x: x[0] != 'ean13', args)
            #add the new criterion
            args += [('ean13_ids', 'in', ean_ids)]
        return super(ProductProduct, self).search(
            cr, uid, args, offset, limit, order, context=context, count=count)
