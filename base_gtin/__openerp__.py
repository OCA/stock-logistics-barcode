# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Base GTIN",
    "summary": "Support GTIN barcode nomenclatures in an abstract way",
    "version": "9.0.1.0.0",
    "author": "LasLabs, "
              "Odoo Community Association (OCA)",
    "website": "https://odoo-community.org/",
    "license": "AGPL-3",
    "category": "Hidden",
    "depends": [
        'barcodes',
    ],
    "data": [
        'views/res_company.xml',
        'views/assets.xml',
    ],
    'test': [
        'static/tests/js/barcode_parser.js',
    ],
    'installable': True,
}
