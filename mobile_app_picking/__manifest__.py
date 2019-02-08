# Copyright (C) 2019-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Picking Mobile App',
    'version': '11.0.1.0.0',
    'category': 'Stock',
    'author': 'GRAP,Odoo Community Association (OCA)',
    'website': 'https://www.odoo-community.org',
    'license': 'AGPL-3',
    'depends': [
        'mobile_app_angular',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/view_stock_picking_type.xml',
    ],
    'demo': [
        'demo/stock_picking_type.xml',
        'demo/stock_picking.xml',
    ],
}
