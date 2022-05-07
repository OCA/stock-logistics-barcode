# Copyright 2019 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Stock Barcodes Move Location",
    "summary": "It provides read barcode on stock operations.",
    "version": "13.0.1.0.1",
    "author": "Tecnativa, " "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-barcode",
    "license": "AGPL-3",
    "category": "Extra Tools",
    "depends": [
        "stock_barcodes",
        "stock_move_location",
        "stock_barcodes_automatic_entry",
    ],
    "data": [
        "views/assets.xml",
        "views/stock_picking_type_views.xml",
        "wizard/stock_move_location_views.xml",
        "wizard/stock_barcodes_read_move_location_views.xml",
    ],
    "installable": True,
}
