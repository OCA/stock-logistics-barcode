# -*- coding: utf-8 -*-
# Copyright 2020 Sunflower IT
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Barcodes - Regex groups",
    "summary": "Partial barcode capture, using regex groups in nomenclatures.",
    "version": "10.0.1.0.0",
    "author": "Sunflower IT, "
              "Odoo Community Association (OCA)",
    "website": "https://odoo-community.org/",
    "license": "AGPL-3",
    "category": "Extra Tools",
    "depends": [
        'barcodes',
    ],
    "data": [
        "views/assets_backend.xml",
        "views/barcode_rule.xml"
    ],
    'installable': True,
}
