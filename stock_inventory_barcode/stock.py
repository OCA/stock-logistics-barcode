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
from openerp.osv import orm
from openerp.tools.translate import _


class stock_inventory(orm.Model):
    _name = 'stock.inventory'
    _inherit = ['stock.inventory', 'product.product.barcode.input']

    def onchange_barcode(self, cr, uid, ids, barcode_input=None,
                         inventory_line_id=None, input_location_id=None,
                         context=None):
        if not input_location_id and barcode_input:
            return {
                'warning': {
                    'title': _('Warning'),
                    'message': _('Please select a location before '
                                 'entering a barcode')
                }
            }
        if context is None:
            context = {}
        context.update({'key_line_ids': 'inventory_line_id',
                        'key_qty': 'product_qty', })
        res = super(stock_inventory, self) \
            .onchange_barcode(cr, uid, ids, barcode_input=barcode_input,
                              line_ids=inventory_line_id,
                              input_location_id=input_location_id,
                              context=context)
        return res
