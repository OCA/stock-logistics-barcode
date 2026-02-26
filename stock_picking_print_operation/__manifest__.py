# Copyright 2026 ACSONE SA/NV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

{
    "name": "Stock Picking Print Operation",
    "summary": """This module allows to individually launch product
    label printings from stock operations""",
    "version": "18.0.1.0.0",
    "license": "LGPL-3",
    "maintainers": ["rousseldenis"],
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-barcode",
    "depends": ["stock"],
    "data": [
        "views/stock_picking_type.xml",
        "views/stock_picking.xml",
        "views/stock_move_line.xml",
        "wizards/product_label_layout.xml",
    ],
}
