# Copyright (C) 2022 Akretion
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": "Sale Input Barcode",
    "version": "14.0.1.0.0",
    "category": "Tools",
    "website": "https://github.com/OCA/stock-logistics-barcode",
    "author": "Akretion, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "summary": "Add Sale line with barcode",
    "maintainers": ["bealdav"],
    "depends": [
        "sale_management",
        "barcode_action",
        "base_gs1_barcode",
    ],
    "data": [
        "views/sale.xml",
    ],
    "demo": [],
}
