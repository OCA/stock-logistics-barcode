# -*- coding: utf-8 -*-
#################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Julius Network Solutions SARL <contact@julius.fr>
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


from openerp.osv import fields, osv
import copy

class tr_barcode_settings(osv.osv_memory):
    _name = 'tr.barcode.settings'
    _inherit = 'res.config.settings'
    _columns = {        'models_ids': fields.many2many('ir.model',
                        'tr_barcode_settings_mode_rel',
                        'tr_id', 'model_id', 'Models'),
                }
    def install(self, cr, uid, ids, context=None):
        
        
#       Initialisation of the configuration
        
        if context is None:
            context = {}
        model_obj = self.pool.get('ir.model')
        action_obj = self.pool.get('ir.actions.act_window')
        value_obj = self.pool.get('ir.values')
        
        """ create method """
        for vals in self.read(cr, uid, ids, context=context):
        
            if not vals or not vals.get('models_ids', False):
                return False
            
#           Supression of the old configuration
            
            unlink_ids = action_obj.search(cr,  uid, [('res_model' , '=', 'tr.barcode.wizard')])
            for unlink_id in unlink_ids:
                action_obj.unlink(cr, uid, unlink_id)
                un_val_ids = value_obj.search(cr, uid,[
                    ('value' , '=',"ir.actions.act_window," + str(unlink_id)),
                    ])
                value_obj.unlink(cr, uid, un_val_ids)
                
            ######################### 
                
            read_datas = model_obj.read(cr, uid, vals['models_ids'], ['model','name'], context=context)
            for model in read_datas:
                act_id = action_obj.create(cr, uid, {
                     'name': "%s Barcode" % model['name'],
                     'type': 'ir.actions.act_window',
                     'res_model': 'tr.barcode.wizard',
                     'src_model': model['model'],
                     'view_type': 'form',
                     'context': "{'src_model':'%s','src_rec_id':active_id,"\
                     "'src_rec_ids':active_ids}" % (model['model']),
                     'view_mode':'form,tree',
                     'target': 'new',
                }, context)
                value_obj.create(cr, uid, {
                 'name': "%s Barcode" % model['name'],
                 'model': model['model'],
                 'key2': 'client_action_multi',
                 'value': "ir.actions.act_window," + str(act_id),
    #             'object': True,
                    }, context)
            
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
    
        
    

tr_barcode_settings()