# -*- coding: utf-8 -*-

{
    'name': 'TR Barcode',
    'version': '1.0',
    'category': 'Generic Modules',
    'description': """
    """,
    'author': 'Tech Receptives',
    'website': 'http://www.techreceptives.com',
    'depends': ["base",
                ],
    'init_xml': [],
    'update_xml': [
        "tr_barcode_installer.xml",
        "tr_barcode_view.xml",
        "wizard/tr_barcode_wizard.xml",
        "security/ir.model.access.csv",
    ],
    'demo_xml': [],
    'test': [
    ],
    'installable': True,
    'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
