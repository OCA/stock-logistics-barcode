# -*- coding: utf-8 -*-
# © 2011-2015 Sylvain Garancher <sylvain.garancher@syleam.fr>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Stock Scanner Shipping',
    'version': '9.0.1.0.0',
    'category': 'Generic Modules/Inventory Control',
    'website': 'https://odoo-community.org/',
    'author': 'SYLEAM,'
              'Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'installable': True,
    'depends': [
        'stock_scanner',
    ],
    'data': [
        'data/Stock.scenario',
        'data/Shipping/Shipping.scenario',
    ],
}
