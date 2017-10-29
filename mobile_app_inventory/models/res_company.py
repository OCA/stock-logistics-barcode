# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    _SELECTION_MOBILE_PRODUCT_LOAD = [
        ('inventory', 'Inventory Products'),
        ('all', 'All Products'),
    ]

    mobile_inventory_product_field_ids = fields.Many2many(
        string='Product Fields', comodel_name='ir.model.fields',
        domain=[('model', 'in', ['product.product'])])

    mobile_inventory_create = fields.Boolean(
        string='Create Inventories via Mobile App', default=True,
        help="By checking this box, users will have the possibility to"
        " create an inventory by the Mobile App. Otherwise, you should"
        " create and prepare the inventory in the back-office")

    mobile_product_cache = fields.Selection(
        string='Load Product via Mobile App', required=True,
        selection=_SELECTION_MOBILE_PRODUCT_LOAD, default='all',
        help="Select the type of cache that will be used for the mobile app"
        " regarding the products. This selection will depend on the size"
        " of your product table, and the quality of the connection during"
        " the inventory.\n"
        " * Inventory : When selecting an inventory, the products of the"
        " inventory will be loaded\n"
        " * All : Will cache after logging, all the products with barcodes\n")

#    @api.model
#    def mobile_get_settings(self):
#        company = self.env.user.company_id
#        return {
#            'mobile_inventory_create': company.mobile_inventory_create,
#            'mobile_product_cache': company.mobile_product_cache,
#        }
