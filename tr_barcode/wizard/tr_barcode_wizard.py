# -*- coding: utf-8 -*-
##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2004-TODAY Tech-Receptives(<http://www.tech-receptives.com>).
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

from openerp.osv import fields, osv, orm
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)
try:
    from reportlab.graphics.barcode import getCodes
except:
    _logger.warning('unable to import reportlab')


def _get_code(self, cr, uid, context=None):
    """get availble code """
    return [(r, r) for r in getCodes()]


class tr_barcode_wizard(orm.TransientModel):
    """ wizard for barcode """
    _name = "tr.barcode.wizard"
    _description = "Barcode Wizard for generic use"

    def _get_val(self, cr, uid, context=None):
        if not context:
            context = {}
        if not context.get('active_model', False) \
           or not context.get('active_id', False):
            return False
        vals = self.pool.get(context['active_model']).browse(cr, uid,
                                                             context['active_id'],
                                                             context=context)
        return vals and vals.x_barcode_id and vals.x_barcode_id.code or False

    _columns = {
        'barcode': fields.char('Barcode', size=256),
        'width':
            fields.integer("Width",
                           help="Leave Blank or 0(ZERO) for default size"),
        'height':
            fields.integer("Height",
                           help="Leave Blank or 0(ZERO) for default size"),
        'hr_form':
            fields.boolean("Human Readable",
                           help="To genrate Barcode In Human readable form"),
        'barcode_type': fields.selection(_get_code, 'Type'),
        'hr_form':
            fields.boolean("Human Readable",
                           help="To genrate Barcode In Human readable form"),
        }

    _defaults = {
        'barcode': _get_val,
        }

    def open_existing(self, cr, uid, ids, context=None):
        """ function will open existing report """
        if not context:
            context = {}
        return {
            'domain':
            "[('res_id','in', [" +
            ','.join(map(str,
                         context.get('active_ids', []))) +
            "]),('res_model', '=', '%s')]"
            % context.get('src_model', False) or
            context['active_model'],
            'name': 'Barcode',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'tr.barcode',
            'view_id': False,
            'type': 'ir.actions.act_window',
            }

    def create_barcode_record(self, cr, uid, ids, context=None):
        """
            creating record with model and res id """
        if not context:
            context = {}
        barcode_pool = self.pool.get('tr.barcode')
        for self_obj in self.browse(cr, uid, ids, context=context):
            if not self_obj.barcode:
                raise osv.except_osv(_('Error'),
                                     _('Please specify code to generate Barcode !'))
            if not self_obj.barcode_type:
                raise osv.except_osv(_('Error'), _('Please Select Type !'))
            cr_id = barcode_pool.create(cr, uid, {
                'code': self_obj.barcode,
                'barcode_type': self_obj.barcode_type,
                'width': self_obj.width,
                'height': self_obj.height,
                'hr_form': self_obj.hr_form,
                'res_model':
                    context.get('src_model', False) or
                    context['active_model'],
                'res_id': context['active_id'],
                })
            barcode_pool.generate_image(cr, uid, [cr_id], context=context)
            return {
                'res_id': cr_id,
                'name': 'Barcode',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'tr.barcode',
                'view_id': False,
                'type': 'ir.actions.act_window',
                }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
