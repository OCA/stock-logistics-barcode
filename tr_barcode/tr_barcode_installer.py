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

from osv import fields, osv
import copy
class tr_barcode_installer(osv.osv_memory):
    """ config wizard for barcode module """
    _name = 'tr_barcode.installer'
    _inherit = 'res.config.installer'

    _columns = {
        'models_ids': fields.many2many('ir.model',
                        'tr_barcode_installer_mode_rel',
                        'tr_id', 'model_id', 'Models'),
    }
    def create(self, cr, uid, vals, context=None):
        """ create method """
        vals2 = copy.deepcopy(vals)
        ret = super(tr_barcode_installer, self).create(cr, uid,
                                                vals2, context=context)
        if not vals or not vals.get('models_ids', False) or not vals.get(
                                                    'models_ids', False)[0][-1]:
            return ret
        unlink_ids = self.pool.get('ir.actions.act_window').search(cr,
                        uid, [('res_model' , '=', 'tr.barcode.wizard')])

        for unlink_id in unlink_ids:

            self.pool.get('ir.actions.act_window').unlink(cr, uid, unlink_id)
            un_val_ids = self.pool.get('ir.values').search(cr, uid,
                    [('value' , '=',
                    "ir.actions.act_window," + str(unlink_id))])
            self.pool.get('ir.values').unlink(cr, uid, un_val_ids)

        read_datas = self.pool.get('ir.model').read(cr, uid,
                vals['models_ids'][0][-1], ['model','name'], context=context)
        for model in read_datas:
            act_id = self.pool.get('ir.actions.act_window').create(cr, uid, {
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
            self.pool.get('ir.values').create(cr, uid, {
             'name': "%s Barcode" % model['name'],
             'model': model['model'],
             'key2': 'client_action_multi',
             'value': "ir.actions.act_window," + str(act_id),
#             'object': True,
                }, context)
        return ret
tr_barcode_installer()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
