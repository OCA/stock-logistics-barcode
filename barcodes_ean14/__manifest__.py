# -*- coding: utf-8 -*-
# Copyright 2016-2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Barcodes - EAN14",
    "summary": "It provides an EAN14 barcode nomenclature.",
    "version": "10.0.1.0.1",
    "author": "LasLabs, "
              "Odoo Community Association (OCA)",
    "website": "https://odoo-community.org/",
    "license": "AGPL-3",
    "category": "Extra Tools",
    "depends": [
        'barcodes',
    ],
    "data": [
        'views/assets.xml',
    ],
    'test': [
        'static/tests/js/barcode_parser.js',
    ],
    'installable': True,
}
