# Copyright 2019 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Stock Barcodes",
    "summary": "It provides read barcode on stock operations.",
    "version": "12.0.2.0.0",
    "author": "Tecnativa, "
              "Odoo Community Association (OCA)",
    "website": "https://odoo-community.org/",
    "license": "AGPL-3",
    "category": "Extra Tools",
    "depends": [
        'stock_barcodes',
        'stock_move_location',
        'stock_barcodes_automatic_entry',
    ],
    "data": [
        'views/assets.xml',
        'wizard/stock_move_location_views.xml',
        'wizard/stock_barcodes_read_move_location_views.xml',
    ],
    'installable': True,
}
