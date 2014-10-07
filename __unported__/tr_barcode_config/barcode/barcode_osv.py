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
from openerp import pooler
from openerp import SUPERUSER_ID


def write_barcode(cr, uid, ids, vals, model, context=None):
    if context is None:
       context = {}
    pool = pooler.get_pool(cr.dbname)
    for id in ids:
        config_obj = pool.get('tr.barcode.config')
        config = config_obj.search(cr, uid,
                                   [('res_model.model', '=', model)])
        if config:
            barcode_config = config_obj.browse(cr, uid, config[0])
            code = vals.get(barcode_config.field.name, False)
            barcode_vals = {
                'code': vals.get(barcode_config.field.name, False),
                'barcode_type': barcode_config.barcode_type,
                'width': barcode_config.width,
                'height': barcode_config.height,
                'hr_form': barcode_config.hr_form,
            }
            if not barcode_vals['code']:
                current_id = False
                if context.get('obj_id'):
                    current_id = context.get('obj_id')
                elif context.get('__copy_data_seen'):
                    current_id = context.get('__copy_data_seen')
                    current_id = current_id.get(model)[0]
                if current_id:
                    data = pool.get(model).read(cr, uid, current_id)
                    if data:
                        code = data[barcode_config.field.name]
                        if code:
                            barcode_vals['code'] = code
                        else:
                            barcode_vals.pop('code')
            barcode_obj = pool.get('tr.barcode')
            barcode_obj.write(cr, uid, [id], barcode_vals, context=context)
            barcode_obj.generate_image(cr, uid, [id], context=context)
    return True


def create_barcode(cr, uid, id, vals, model, context=None):
    if context is None:
       context = {}
    pool = pooler.get_pool(cr.dbname)
    config_obj = pool.get('tr.barcode.config')
    if not context.get('__copy_data_seen'):
        barcode_id = vals.get('x_barcode_id', False)
    else:
        barcode_id = False
    if not barcode_id:
        config = config_obj.search(cr, uid,
                                   [('res_model.model', '=', model)])
        if config:
            barcode_config = config_obj.browse(cr, uid, config[0])
            barcode_vals = {
                'code': vals.get(barcode_config.field.name, False),
                'res_model': model,
                'res_id': id,
                'barcode_type': barcode_config.barcode_type,
                'width': barcode_config.width,
                'height': barcode_config.height,
                'hr_form': barcode_config.hr_form,
            }
            if not barcode_vals.get('code', False):
                read_value = pool.get(model).read(cr, uid, id)
                barcode_vals['code'] = read_value.get(barcode_config.field.name, False)
            barcode_obj = pool.get('tr.barcode')
            barcode_id = barcode_obj.create(cr, uid, barcode_vals, context=context)
            barcode_obj.generate_image(cr, uid, [barcode_id], context=context)
    else:
        write_barcode(cr, uid, [barcode_id], vals, model, context=context)
    return barcode_id


class barcode_osv(orm.Model):
    _register = False

    def __init__(self, pool, cr):
        installer_obj = pool.get('tr.barcode.settings')
        model_obj = pool.get('ir.model')
        uid = SUPERUSER_ID
        model_ids = model_obj.search(cr, uid, [('model', '=', self._name)])
        installer_obj.create(cr, uid,
                             {'models_ids': [(6, 0, model_ids)]},
                             context=None)
        super(barcode_osv, self).__init__(pool, cr)

    def create(self, cr, uid, vals, context=None):
        barcode_id = False
        res = super(orm.Model, self).create(cr, uid, vals, context=context)

        # modification because the orm create method seems to go into the
        # write method so there is 2 barcode created instead of one
        obj = self.browse(cr, uid, res, context=context)
        if hasattr(obj, 'x_barcode_id'):
            if not obj.x_barcode_id:
                barcode_id = create_barcode(cr, uid, res, vals, self._name, context=context)
            else:
                barcode_id = obj.x_barcode_id.id
        # end modification

            if barcode_id:
                query = "UPDATE %s SET x_barcode_id = %%s WHERE id = %%s" % self._table
                cr.execute(query, (barcode_id, res))
        return res

    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = {}
        if type(ids) in (type(1), type(1L), type(1.0)):
            ids = [ids]
        barcode_obj = self.pool.get('tr.barcode')
        for obj in self.browse(cr, uid, ids, context=context):
            context.update({'obj_id': obj.id})
            if not hasattr(obj, 'x_barcode_id'):
                break  # the module is not fully configured, quick exit
            if not obj.x_barcode_id:
                barcode_ids = barcode_obj.search(cr, uid,
                                                 [('res_model', '=', self._name),
                                                  ('res_id', '=', obj.id)
                                                  ],
                                                 limit=1,
                                                 context=context)
                if barcode_ids:
                    write_barcode(cr, uid,
                                  [barcode_ids[0]],
                                  vals,
                                  self._name,
                                  context=context)
                    vals['x_barcode_id'] = barcode_ids[0]
                else:
                    barcode_id = create_barcode(cr, uid,
                                                obj.id,
                                                vals,
                                                self._name,
                                                context=context)
                    if barcode_id:
                        vals['x_barcode_id'] = barcode_id
            else:
                write_barcode(cr, uid,
                              [obj.x_barcode_id.id],
                              vals,
                              self._name,
                              context=context)
        return super(orm.Model, self).write(cr, uid, ids, vals, context=context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
