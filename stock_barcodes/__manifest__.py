# Copyright 2019 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Stock Barcodes",
    "summary": "It provides read barcode on stock operations.",
    "version": "12.0.2.3.0",
    "author": "Tecnativa, "
              "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-barcode",
    "license": "AGPL-3",
    "category": "Extra Tools",
    "depends": [
        "barcodes",
        "stock",
    ],
    "data": [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/assets.xml',
        'views/res_config_settings_views.xml',
        'views/stock_inventory_views.xml',
        'views/stock_picking_views.xml',
        'wizard/stock_production_lot_views.xml',
        'wizard/stock_barcodes_read_views.xml',
        'wizard/stock_barcodes_read_inventory_views.xml',
        'wizard/stock_barcodes_read_picking_views.xml',
        'templates/missing_moves_template.xml',
    ],
    "installable": True,
}
