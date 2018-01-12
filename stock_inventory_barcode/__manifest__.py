# -*- coding: utf-8 -*-
# © 2015-2018 Akretion (http://www.akretion.com)
# @author Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': "Barcode Input for Inventories",
    'version': "10.0.0.1.0",
    'category': "Inventory, Logistic, Storage",
    'author': 'Akretion,Odoo Community Association (OCA)',
    'summary': "Add simple barcode interface on inventories",
    'license': 'AGPL-3',
    'depends': ['stock'],
    'data': [
        'wizard/stock_inventory_barcode_view.xml',
        'views/stock_inventory.xml',
        ],
    'installable': True,
}
