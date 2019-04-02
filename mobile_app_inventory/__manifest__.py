# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Inventory Mobile App',
    'version': '11.0.1.0.0',
    'summary': """
    Perform a full inventory from a mobile device with
    barcode reader
    """,
    'category': 'Inventory, Logistics, Warehousing',
    'author': 'GRAP,Akretion,Odoo Community Association (OCA)',
    'website': 'https://www.odoo-community.org',
    'license': 'AGPL-3',
    'depends': [
        'stock',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/view_stock_inventory.xml',
        'views/view_stock_location.xml',
        'views/view_stock_config_settings.xml',
    ],
    'demo': [
        'demo/res_users.xml',
        'demo/res_company.xml',
        'demo/stock_location.xml',
        'demo/stock_inventory.xml',
        'demo/product_product.xml',
    ],
    'post_init_hook': 'set_mobile_available_on_stock_location',
}
