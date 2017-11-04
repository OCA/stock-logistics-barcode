# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    mobile_available = fields.Boolean(
        string='Available on Mobile', default=True,
        help="Check this box if you want that a user making an inventory"
        " by the Mobile App can work on this inventory.")

    unknown_line_ids = fields.One2many(
        comodel_name='stock.inventory.unknown.line',
        string='Unknown Barcode Lines', inverse_name='inventory_id')

    unknown_line_qty = fields.Integer(
        string='Unknown Barcode Lines Quantity', store=True,
        compute='_compute_unknown_line_qty')

    @api.multi
    @api.depends('unknown_line_ids.barcode')
    def _compute_unknown_line_qty(self):
        for inventory in self:
            inventory.unknown_line_qty = len(inventory.unknown_line_ids)
