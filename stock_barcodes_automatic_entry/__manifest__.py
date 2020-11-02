# Copyright 2020 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Stock Barcodes Automatic Entry",
    "summary": """
        This module will automatically trigger the click event on a button
        with the class 'barcode-automatic-entry' after a barcode scanned has
        been processed.
    """,
    "version": "13.0.1.0.1",
    "license": "AGPL-3",
    "maintainers": ["AdriaGForgeFlow"],
    "author": "ForgeFlow S.L., Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-barcode",
    "depends": ["barcodes"],
    "data": ["views/assets.xml"],
}
