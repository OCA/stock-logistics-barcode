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
    _columns = {
        'models_ids': fields.many2many('ir.model',
            'tr_barcode_settings_mode_rel',
            'tr_id', 'model_id', 'Models'),
    }
    
    def update_field(self, cr, uid, vals, context=None):
        ## Init ##
        if context is None:
            context = {}
        model_ids = []
        model_obj = self.pool.get('ir.model')
        action_obj = self.pool.get('ir.actions.act_window')
        value_obj = self.pool.get('ir.values')
        ## Process ##
        if not vals or not vals.get('models_ids', False):
            return False
        elif vals['models_ids'][0] and vals['models_ids'][0][2]:
            model_ids = vals['models_ids'][0][2]
        ### Unlink Previous Entries ###
        unlink_ids = action_obj.search(cr,  uid, [('res_model' , '=', 'tr.barcode.wizard')])
        for unlink_id in unlink_ids:
            action_obj.unlink(cr, uid, unlink_id)
            un_val_ids = value_obj.search(cr, uid,[
                ('value' , '=',"ir.actions.act_window," + str(unlink_id)),
                ])
            value_obj.unlink(cr, uid, un_val_ids)
            
        ### Create New Fields ###
        read_datas = model_obj.read(cr, uid, model_ids, ['model','name'], context=context)
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
            }, context)
            
        return True
    
    def create(self, cr, uid, vals, context=None):
        """ create method """
        vals2 = copy.deepcopy(vals)
        result = super(tr_barcode_settings, self).create(cr, uid, vals2, context=context)
        ## Fields Process ##
        self.update_field(cr, uid, vals, context=context)
        return result
    
    def install(self, cr, uid, ids, context=None):
#       Initialisation of the configuration
        if context is None:
            context = {}
        """ install method """
        for vals in self.read(cr, uid, ids, context=context):
            result = self.update_field(cr, uid, vals, context=context)
            
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

tr_barcode_settings()