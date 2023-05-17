# Copyright 2020 Lorenzo Battistini @ TAKOBI
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Stock barcodes - Supplier pricelist",
    "summary": "Process products searching them by supplier barcode",
    "version": "12.0.1.0.2",
    "development_status": "Beta",
    "category": "Extra Tools",
    "website": "https://github.com/OCA/stock-logistics-barcode",
    "author": "TAKOBI, Odoo Community Association (OCA)",
    "maintainers": ["eLBati"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "preloadable": True,
    "auto_install": True,
    "depends": [
        "product_supplierinfo_barcode",
        "stock_barcodes",
    ],
    "data": [
    ],
    "demo": [
    ],
}
