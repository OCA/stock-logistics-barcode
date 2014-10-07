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

from openerp.osv import fields, orm


class tr_barcode(orm.Model):

    _inherit = 'tr.barcode'

    def _name_get_barcode(self, cr, uid, ids, field_name, arg=None, context=None):
        if not len(ids):
            return []
        reads = self.browse(cr, uid, ids, context=context)
        res = {}
        for record in reads:
            link = ''
            if record.res_model and record.res_id:
                link = record.res_model + ',' + str(record.res_id)
            res[record.id] = link
        return res

    _columns = {
        'link': fields.function(_name_get_barcode,
                                method=True,
                                type='char',
                                size=100,
                                string="Link"),
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
