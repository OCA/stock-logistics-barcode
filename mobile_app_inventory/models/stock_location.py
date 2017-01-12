# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.osv import fields
from openerp.osv.orm import Model


class StockLocation(Model):
    _inherit = 'stock.location'

    # Compute Section
    def compute_parent_complete_name(
            self, cr, uid, ids, name, args, context=None):
        res = {}
        for location in self.browse(cr, uid, ids, context=context):
            if location.location_id:
                res[location.id] = location.location_id.complete_name
            else:
                res[location.id] = ''
        return res

    # Columns Section
    _columns = {
        'parent_complete_name': fields.function(
            compute_parent_complete_name, string='Parent Complete Name',
            type='char'),
    }
