# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class StockLocation(models.Model):
    _inherit = 'stock.location'

    # Columns Section
#    parent_complete_name = fields.Char(
#        compute='_compute_parent_complete_name', string='Parent Complete Name')

    mobile_available = fields.Boolean(
        string='Available for Mobile', default=True,
        help="Check this box if you want to make this location visible"
        " in the Mobile App")

#    # Compute Section
#    @api.depends('name', 'location_id')
#    def _compute_parent_complete_name(self):
#        for location in self:
#            location.parent_complete_name =\
#                location.location_id and\
#                location.location_id.complete_name or ''

    # Onchange Section
    @api.onchange('usage')
    def onchange_location_type(self):
        self.mobile_available = self.usage == 'internal'
