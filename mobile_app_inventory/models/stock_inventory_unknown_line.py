# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models
from odoo.addons import decimal_precision as dp


class StockInventoryUnknownLine(models.Model):
    _name = 'stock.inventory.unknown.line'

    inventory_id = fields.Many2one(
        comodel_name='stock.inventory', required=True, ondelete='cascade',
        string='Inventory')

    barcode = fields.Char(string='Barcode', required=True, readonly=True)

    quantity = fields.Float(
        string='Quantity', readonly=True,
        digits=dp.get_precision('Product Unit of Measure'))
