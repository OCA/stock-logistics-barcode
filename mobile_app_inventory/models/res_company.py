# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    mobile_inventory_product_field_ids = fields.Many2many(
        string='Product Fields', comodel_name='ir.model.fields',
        domain=[('model', 'in', ['product.product'])])

    mobile_inventory_create = fields.Boolean(
        string='Create Inventories via Mobile App', default=True,
        help="By checking this box, users will have the possibility to"
        " create an inventory by the Mobile App. Otherwise, you should"
        " create and prepare the inventory in the back-office")
