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

from openerp.osv import fields, orm
import copy


class tr_barcode_installer(orm.TransientModel):
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
        _super = super(tr_barcode_installer, self)
        ret = _super.create(cr, uid,
                            vals2,
                            context=context)
        if not vals \
           or not vals.get('models_ids') \
           or not vals.get('models_ids', False)[0][-1]:
            return ret
        act_window = self.pool.get('ir.actions.act_window')
        ir_value = self.pool.get('ir.values')
        ir_model = self.pool.get('ir.model')
        unlink_ids = act_window.search(cr,
                                       uid,
                                       [('res_model', '=', 'tr.barcode.wizard')])

        for unlink_id in unlink_ids:

            act_window.unlink(cr, uid, unlink_id)
            domain = [('value', '=', "ir.actions.act_window,%s" % unlink_id)]
            un_val_ids = ir_value.search(cr, uid,
                                         domain)
            ir_value.unlink(cr, uid, un_val_ids)

        read_datas = ir_model.read(cr, uid,
                                   vals['models_ids'][0][-1],
                                   ['model', 'name'],
                                   context=context)
        for model in read_datas:
            vals = {'name': "%s Barcode" % model['name'],
                    'type': 'ir.actions.act_window',
                    'res_model': 'tr.barcode.wizard',
                    'src_model': model['model'],
                    'view_type': 'form',
                    'context': "{'src_model':'%s','src_rec_id':active_id,"
                    "'src_rec_ids':active_ids}" % (model['model']),
                    'view_mode': 'form,tree',
                    'target': 'new',
                    }
            act_id = act_window.create(cr, uid,
                                       vals,
                                       context=context)
            vals = {'name': "%s Barcode" % model['name'],
                    'model': model['model'],
                    'key2': 'client_action_multi',
                    'value': "ir.actions.act_window,%s" % act_id,
                    #             'object': True,
                    }
            ir_value.create(cr, uid, vals, context=context)
        return ret

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
