# Copyright 2020 Manuel Calero - Xtendoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Stock Barcodes Internal Transfer",
    "summary": "It provides read barcode for internal transfers.",
    "version": "12.0.1.0.0",
    "author": "Xtendoo, "
              "Odoo Community Association (OCA)",
    "website": "https://odoo-community.org/",
    "license": "AGPL-3",
    "category": "Extra Tools",
    "depends": [
        'stock_barcodes',
    ],
    "data": [
        'views/stock_picking_views.xml',
        'wizard/stock_barcodes_read_internal_transfer_views.xml'
    ],    
    'installable': True,
}
