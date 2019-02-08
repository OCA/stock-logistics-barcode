# Copyright (C) 2019-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    mobile_available = fields.Boolean(
        string='Available on Mobile',
        help="Check this box if you want to make this picking type visible"
        " on the Mobile App")

    mobile_backorder_create = fields.Boolean(
        string='Mobile - Create Backorder', default=True,
        help="Check this box if you want that confirming a picking on mobile"
        " app generate a backorder by default.")
