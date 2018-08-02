# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    _MOBILE_INVENTORY_MODE_SELECTION = [
        ('automate', 'Automate'),
        ('one_page', 'One Page'),
    ]

    mobile_inventory_product_field_ids = fields.Many2many(
        string='Product Fields', comodel_name='ir.model.fields',
        domain=[('model', 'in', ['product.product'])])

    mobile_inventory_create = fields.Boolean(
        string='Create Inventories via Mobile App', default=True,
        help="By checking this box, users will have the possibility to"
        " create an inventory by the Mobile App. Otherwise, you should"
        " create and prepare the inventory in the back-office")

    mobile_inventory_mode = fields.Selection(
        selection=_MOBILE_INVENTORY_MODE_SELECTION,
        string='Mobile App Inventory Mode', default='automate',
        help="Mode of the Mobile App UI:\n"
        " * 'Automate': The UI will display one screen per action."
        " (select a product, set a quantity, etc...\n"
        " * 'One page': A single page will let the user scan a product or"
        " a location or set a quantity in a single input field")

    mobile_inventory_allow_unknown = fields.Boolean(
        string='Allown Unknown Barcodes', default=False,
        help="By checking this box, users will have the possibility to"
        " scan unknown barcodes. The quantities and the barcodes will be"
        " displayed in an extra tabs, in the inventory view. If unchecked,"
        " an error message will be displayed to the user if he scans"
        " unknown barcode")
