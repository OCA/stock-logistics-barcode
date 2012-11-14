# -*- coding: utf-8 -*-

{
    'name': 'TR Barcode',
    'version': '1.0',
    'category': 'Generic Modules',
    'description': """

Presentation:

This module adds the menu Barcode used to generate and configuration barcodes.
    
    """,
    'author': 'Tech Receptives',
    'website': 'http://www.techreceptives.com',
    'depends': [
        "base",
    ],
    'init_xml': [],
    'update_xml': [
        "tr_barcode_installer.xml",
        "tr_barcode_view.xml",
        "wizard/tr_barcode_wizard.xml",
        "security/ir.model.access.csv",
    ],
    'demo_xml': [],
    "images" : ['images/Barcode configuration.png','images/Barcode.png'],
    'test': [
    ],
    'installable': True,
    'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
