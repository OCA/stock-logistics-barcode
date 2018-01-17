# -*- coding: utf-8 -*-
# © 2018 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, SUPERUSER_ID


def set_mobile_available_on_stock_location(cr, registry):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        internal_locs = env['stock.location'].search(
            [('usage', '=', 'internal')])
        internal_locs.write({'mobile_available': True})
    return
