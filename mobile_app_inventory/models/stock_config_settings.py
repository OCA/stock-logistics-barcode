# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockConfigSettings(models.TransientModel):
    _inherit = 'stock.config.settings'

    mobile_inventory_product_field_ids = fields.Many2many(
        related='company_id.mobile_inventory_product_field_ids')
    mobile_inventory_create = fields.Boolean(
        related='company_id.mobile_inventory_create')
