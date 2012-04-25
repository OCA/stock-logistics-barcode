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

from osv import osv,fields
from tools.translate import _

class stock_reference(osv.osv_memory):

    _name = "stock.reference"
    _description = 'Products Acquisition'
    
#    _rec_name = 'reference'
    
    def _get_track_id(self, cr, uid, context=None):
        if context == None:
            context = {}
        return context.get('active_id',False)
    
    _columns = {
#        'barcode_id': fields.many2one('tr.barcode', 'Reference', required=True),
        'reference': fields.char('Reference', size=128, required=True),
        'track_id': fields.many2one('acquisition.acquisition','Track id', required=True),
        'text': fields.text('Barcode list',readonly=True),
#        'bad_barcode': fields.text('Bad barcode list',readonly=True),
    }

    _defaults = {
        'track_id': _get_track_id,
    }
           
    def onchange_reference(self, cr, uid, ids, reference, track_id, barcode_list=''):        

        res = {}
        barcode_obj = self.pool.get('tr.barcode')
        acquisition_list = self.pool.get('acquisition.list')
        acquisition_setting = self.pool.get('acquisition.setting')        
        
        text = barcode_list or ''
        
        if reference:
            barcode_ids = barcode_obj.search(cr, uid, [('code', '=', reference)], limit=1)
            if not barcode_ids:
                reference2 = reference
                while len(reference2.split('-')) > 1:
                    reference2 = reference2.replace('-','')
                barcode_ids = barcode_obj.search(cr, uid, [('code2', '=', reference2)], limit=1)
            
            if barcode_ids:                    
                barcode_type = 'object'
                line_ids = acquisition_list.search(cr, uid, [('barcode_id', '=', barcode_ids[0]), ('acquisition_id', '=', track_id)])
                setting_ids = acquisition_setting.search(cr, uid, [('barcode_id', '=', barcode_ids[0])], limit=1)
                
                if setting_ids:
                    setting_data = acquisition_setting.browse(cr, uid, setting_ids)                    
                    barcode_type = setting_data[0].action_type
                create = True
                if line_ids:
                    create = False
                    line_barcode = barcode_obj.read(cr, uid, barcode_ids[0], ['res_model'])
                    if line_barcode.get('res_model',False) == 'product.product' or setting_ids:
                        create = True
                if create:
                    acquisition_list.create(cr, uid, {
                        'barcode_id': barcode_ids[0],
                        'acquisition_id': track_id,
                        'type': barcode_type,
                        })        
                    text = reference + '\n' + text
                
            else:
                raise osv.except_osv(_('Warning!'),_('Barcode Not found!')) # Return of the wraning msg !!
##                bad_barcode = bad_barcode_list or ''         
#                bad_barcode += reference
#                if bad_barcode:
#                        bad_barcode += '\n'

            
        return {'value': {'reference' : False, 'text' : text}}          

stock_reference()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: