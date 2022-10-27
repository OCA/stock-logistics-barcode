# Copyright 2020 Lorenzo Battistini @ TAKOBI
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "Barcode in supplier pricelist",
    "summary": "Add a barcode to supplier pricelist items",
    "version": "14.0.1.1.0",
    "development_status": "Beta",
    "category": "Hidden",
    "website": "https://github.com/OCA/stock-logistics-barcode",
    "author": "TAKOBI, Odoo Community Association (OCA)",
    "maintainers": ["eLBati"],
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "preloadable": True,
    "depends": [
        # we need purchase to view seller_ids in product form
        "purchase",
    ],
    "data": [
        "views/supplierinfo_views.xml",
        "views/product_views.xml",
    ],
    "demo": [],
}
