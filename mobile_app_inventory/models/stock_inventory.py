# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    mobile_available = fields.Boolean(
        string='Available on Mobile', default=True,
        help="Check this box if you want that a user making an inventory"
        " by the Mobile App can work on this inventory.")
