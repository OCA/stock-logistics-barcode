# Copyright 2020-2022 Therp BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Barcodes - Multiline",
    "summary": "Allow keyboard-wedge scanners to read multiline barcodes",
    "version": "19.0.1.0.0",
    "author": "Therp BV, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-barcode",
    "license": "AGPL-3",
    "category": "Extra Tools",
    "depends": ["barcodes"],
    "data": ["security/ir.model.access.csv"],
    "demo": ["demo/demo_wizard.xml"],
    "assets": {
        "web.assets_backend": [
            "barcodes_multiline/static/src/js/barcode_multiline_service.esm.js",
        ],
        "web.assets_unit_tests": [
            "barcodes_multiline/static/src/js/barcode_multiline_service.esm.js",
            "barcodes_multiline/static/tests/barcode_multiline.test.js",
        ],
    },
    "installable": True,
}
