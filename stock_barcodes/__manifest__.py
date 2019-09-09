# Copyright 2019 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Stock Barcodes",
    "summary": "It provides read barcode on stock operations.",
    "version": "11.0.1.1.0",
    "author": "Tecnativa, "
              "Odoo Community Association (OCA)",
    "website": "https://odoo-community.org/",
    "license": "AGPL-3",
    "category": "Extra Tools",
    "depends": [
        'barcodes',
        'stock',
    ],
    "data": [
        'security/ir.model.access.csv',
        'views/assets.xml',
        'views/stock_inventory_views.xml',
        'views/stock_picking_views.xml',
        'wizard/stock_production_lot_views.xml',
        'wizard/stock_barcodes_read_views.xml',
        'wizard/stock_barcodes_read_inventory_views.xml',
        'wizard/stock_barcodes_read_picking_views.xml',
    ],
    'installable': True,
}
