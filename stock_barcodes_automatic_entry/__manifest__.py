# Copyright 2020 ForgeFlow S.L.
# Copyright 2026 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Stock Barcodes Automatic Entry",
    "summary": """
        This module will automatically trigger the click event on a button
        with the class 'barcode-automatic-entry' after a barcode scanned has
        been processed.
    """,
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "maintainers": ["AdriaGForgeFlow"],
    "author": "ForgeFlow S.L., Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-barcode",
    "depends": ["barcodes"],
    "assets": {
        "web.assets_backend": [
            "stock_barcodes_automatic_entry/static/src/js/stock_barcodes_automatic_entry.esm.js",
        ],
    },
}
