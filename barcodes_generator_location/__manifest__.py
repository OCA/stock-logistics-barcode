# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Generate Barcodes for Stock Locations",
    "version": "16.0.1.0.0",
    "category": "Tools",
    "author": "LasLabs, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-barcode",
    "license": "AGPL-3",
    "depends": ["barcodes_generator_abstract", "stock"],
    "data": ["views/stock_location.xml"],
    "demo": [
        "demo/ir_sequence.xml",
        "demo/barcode_rule.xml",
        "demo/stock_location.xml",
        "demo/function.xml",
    ],
    "uninstall_hook": "uninstall_hook",
}
