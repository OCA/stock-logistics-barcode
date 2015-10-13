# -*- coding: utf-8 -*-
#################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 Julius Network Solutions SARL <contact@julius.fr>
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
#################################################################################
import logging

from openerp.osv import fields, orm

_logger = logging.getLogger(__name__)
try:
    from reportlab.graphics.barcode import getCodes
except ImportError:
    _logger.warning('unable to import reportlab')


def _get_code(self, cr, uid, context=None):
    """get availble code """
    return [(r, r) for r in getCodes()]


class tr_barcode_config(orm.Model):
    _name = 'tr.barcode.config'
    _columns = {
        'res_model': fields.many2one('ir.model', 'Object',
                                     domain=[('barcode_model', '=', True)],
                                     required=True),
        'field': fields.many2one('ir.model.fields', 'Field',
                                 domain=[('ttype', '=', 'char')],
                                 required=True),
        'width':
            fields.integer("Width",
                           help="Leave Blank or 0(ZERO) for default size"),
        'height':
            fields.integer("Height",
                           help="Leave Blank or 0(ZERO) for default size"),
        'hr_form':
            fields.boolean("Human Readable",
                           help="To generate Barcode In Human readable form"),
        'barcode_type': fields.selection(_get_code, 'Type', required=True),
        }
    _sql_constraints = [
        ('res_model_uniq',
         'unique(res_model)',
         'You can have only one config by model !'),
        ]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
