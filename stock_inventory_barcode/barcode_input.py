# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 initOS GmbH & Co. KG (<http://www.initos.com>).
#    Author Katja Matthes <katja.matthes at initos.com>
#           Thomas Rehn <thomas.rehn at initos.com>
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
from openerp.osv import orm, fields
from openerp.tools.translate import _


class abtract_product_barcode_input(orm.AbstractModel):
    _name = 'abstract.product.barcode.input'
    _description = 'Abstract class to handle barcode input'

    _columns = {
        'barcode_input': fields.char('Barcode', size=128),
        'input_location_id': fields.many2one('stock.location',
                                             'Location for Barcode Input'),
    }

    def find_product(self, cr, uid, barcode_input, context=None):
        """Returns a list of ids of products that match a given barcode"""
        return self.pool.get('product.product') \
            .search(cr, uid, [('ean13', '=', barcode_input)], context=context)

    def onchange_barcode(self, cr, uid, ids, barcode_input=None,
                         line_ids=None, input_location_id=None,
                         context=None):
        """Adds product identified by barcode to a list of lines containing
           a pair of (qty, product_id). The field names to use are
           determined by key_{line_ids,qty,product_id,product_uom}
           values in context."""
        if not barcode_input:
            return {}
        product_ids = self.find_product(cr, uid, barcode_input,
                                        context=context)
        if not product_ids:
            return {
                'warning': {
                    'title': _('Warning'),
                    'message': _('Unknown barcode %s') % barcode_input
                }
            }
        if len(product_ids) > 1:
            return {
                'warning': {
                    'title': _('Warning'),
                    'message':
                        _('Multiple products match barcode %s') % barcode_input
                }
            }

        # set key names of result dict
        # Barcode line input can be used by different models, so the field
        # names may vary.
        if context is None:
            context = {}
        key_line_ids = context.get('key_line_ids', 'inventory_line_id')
        key_product_id = context.get('key_product_id', 'product_id')
        key_product_uom = context.get('key_product_uom', 'product_uom')
        key_qty = context.get('key_qty', 'product_qty')

        product_id = product_ids[0]
        line_exists = False
        for l in line_ids:
            if l[0] != 0:  # skip already saved lines, only modify new lines
                continue
            location_matches = ((not input_location_id) or
                                input_location_id == l[2].get('location_id',
                                                              -1))
            if l[2][key_product_id] == product_id and location_matches:
                l[2][key_qty] += 1
                line_exists = True
                break
        if not line_exists:
            uom_id = self.pool.get('product.product') \
                .browse(cr, uid, product_id).uom_id.id
            line_dict = {key_product_id: product_id,
                         key_qty: 1,
                         key_product_uom: uom_id}
            # set location_id if given, e.g. if used by inventory
            if input_location_id:
                line_dict['location_id'] = input_location_id
            line_ids.append([0, False, line_dict])
        return {'value': {'barcode_input': '',
                          key_line_ids: line_ids}
                }
