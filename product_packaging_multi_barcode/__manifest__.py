# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Multiple barcodes on product packagings",
    "version": "16.0.1.2.0",
    "license": "AGPL-3",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "category": "Product Management",
    "depends": ["product_multi_barcode", "product_multi_barcode_stock_menu"],
    "website": "https://github.com/OCA/stock-logistics-barcode",
    "data": [
        "views/product_packaging_view.xml",
        "views/product_template_view.xml",
        "views/barcode_view.xml",
    ],
    "installable": True,
    "post_init_hook": "post_init_hook",
}
