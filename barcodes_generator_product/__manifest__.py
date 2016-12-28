# -*- coding: utf-8 -*-
# Copyright (C) 2014-Today GRAP (http://www.grap.coop)
# Copyright (C) 2016-Today La Louve (http://www.lalouve.net)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Generate Barcodes for Products',
    'summary': 'Generate Barcodes for Products (Templates and Variants)',
    'version': '10.0.1.0.0',
    'category': 'Tools',
    'author':
        'GRAP,'
        'La Louve,'
        'Odoo Community Association (OCA)',
    'website': 'https://www.odoo-community.org',
    'license': 'AGPL-3',
    'depends': [
        'barcodes_generator_abstract',
        'product',
    ],
    'data': [
        'views/view_product_product.xml',
        'views/view_product_template.xml',
    ],
    'demo': [
        'demo/res_users.xml',
        'demo/barcode_rule.xml',
        'demo/product.xml',
        'demo/function.xml',
    ],
}
