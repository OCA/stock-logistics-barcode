# Copyright Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Stock Barcodes Move Location",
    "summary": "This module allows to move stock between locations using"
               "a barcode scanner.",
    "version": "11.0.1.0.0",
    "author": "Eficent, "
              "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-barcode",
    "license": "AGPL-3",
    "category": "Extra Tools",
    "depends": [
        'stock_barcodes',
        'stock_move_location',
    ],
    "data": [
        'views/assets.xml',
        'wizard/stock_move_location_views.xml',
        'wizard/stock_barcodes_read_move_location_views.xml',
    ],
    'installable': True,
}
