# -*- coding: utf-8 -*-
# © 2016 ONESTEiN BV (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Disable Barcode Interface',
    'category': 'Warehouse Management',
    'version': '8.0.1.0.0',
    'author': 'ONESTEiN BV, Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'website': 'http://www.onestein.eu',
    'depends': ['stock'],
    'data': [
        'security/stock_disable_barcode_interface_security.xml',
        'views/stock_config_settings_view.xml',
        'views/stock_picking_view.xml',
        'views/stock_picking_type_view.xml',
    ],
    'summary': 'Disable and enable (configurable) the barcode interface'
}
