# -*- coding: utf-8 -*-
#/#############################################################################
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
#/#############################################################################

from osv import osv, fields
from tools.translate import _
try:
    from reportlab.graphics.barcode import createBarcodeDrawing, \
            getCodes
except :
    print "ERROR IMPORTING REPORT LAB"

def _get_code(self, cr, uid, context=None):
    """get availble code """
    return [(r, r) for r in getCodes()]

class tr_barcode_wizard(osv.osv_memory):
    """ wizard for barcode """
    _name = "tr.barcode.wizard"
    _description = "Barcode Wizard for generic use"
    def _get_val(self, cr, uid, context=None):
        if not context:
            context = {}
        if not context.get('active_model',False) or not context.get('active_id',False):
            return False
        vals = self.pool.get(context['active_model']).name_get(cr, uid, [context['active_id']], context=context)
        
        return vals[0][-1]
    _columns = {
        'barcode':fields.char('Barcode',size=256),
        'width':fields.integer("Width",
                help="Leave Blank or 0(ZERO) for default size"),
        'hight':fields.integer("Hight",
                help="Leave Blank or 0(ZERO) for default size"),
        'hr_form':fields.boolean("Human Readable",
                help="To genrate Barcode In Human readable form"),
        'barcode_type':fields.selection(_get_code, 'Type'),
        'hr_form':fields.boolean("Human Readable",
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
            'domain': "[('res_id','in', ["+','.join(map(str,
                        context.get('active_ids',[])))+\
                        "]),('res_model', '=', '%s')]"\
                        %context.get('src_model',False) or \
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
                raise osv.except_osv(_('Error'), _('Please specify code to generate Barcode !'))
            if not self_obj.barcode_type:
                raise osv.except_osv(_('Error'), _('Please Select Type !'))
            cr_id = barcode_pool.create(cr, uid, {
                'code':self_obj.barcode,
                'barcode_type':self_obj.barcode_type,
                'width':self_obj.width,
                'hight':self_obj.hight,
                'hr_form':self_obj.hr_form,
                'res_model':context.get('src_model',False) or \
                            context['active_model'],
                'res_id':context['active_id'],
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

    
tr_barcode_wizard()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
