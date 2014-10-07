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

from openerp.osv import orm


class tr_barcode_installer(orm.TransientModel):
    _inherit = 'tr.barcode.settings'

    def install(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if not ids:
            return False
        model_obj = self.pool.get('ir.model')
        field_obj = self.pool.get('ir.model.fields')
        for vals in self.read(cr, uid, ids, context=context):
            if not vals or not vals.get('models_ids', False):
                return False
        read_datas = model_obj.read(cr, uid,
                                    vals['models_ids'],
                                    ['model', 'name'],
                                    context=context)
        for model in read_datas:
            domain = [('name', '=', 'x_barcode_id'),
                      ('model', '=', model['model']),
                      ]
            field_ids = field_obj.search(cr, uid, domain)
            if not field_ids:
                data_field = {'model': model['model'],
                              'relation': 'tr.barcode',
                              'model_id': model['id'],
                              'name': 'x_barcode_id',
                              'field_description': 'Barcode',
                              'state': 'manual',
                              'ttype': 'many2one',
                              'selection': False,
                              'on_delete': 'set null',
                              }
                field_obj.create(cr, uid, data_field, context=context)
        return {'type': 'ir.actions.client',
                'tag': 'reload',
                }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
