# -*- coding: utf-8 -*-
# Copyright 2012 Numérigraphe SARL. All Rights Reserved.
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl).

{
    'name': 'Decoding API for GS1-128 (aka UCC/EAN-128) and GS1-Datamatrix',
    'version': '10.0.1.0.0',
    'author': 'Numérigraphe, Odoo Community Association (OCA)',
    'website': 'http://numerigraphe.com',
    'category': 'Warehouse',
    'summary': """
This module provides an API to decoding the content of structured barcodes
like GS1-128 or GS1-Datamatrix.
""",
    'depends': [
        'product',
    ],
    'data': [
        'views/gs1_barcode_view.xml',
        'views/res_users_view.xml',
        'data/gs1_barcode.csv',
        "security/ir.model.access.csv",
    ],
    'installable': True,
    'license': 'GPL-3',
}
