# Copyright 2019 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Stock Barcodes",
    "summary": "It provides read barcode on stock operations.",
    "version": "14.0.1.2.2",
    "author": "Tecnativa, " "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-barcode",
    "license": "AGPL-3",
    "category": "Extra Tools",
    "depends": ["barcodes", "stock", "web_widget_numeric_step"],
    "data": [
        "security/ir.model.access.csv",
        "data/stock_barcodes_action.xml",
        "data/stock_barcodes_option.xml",
        "views/assets.xml",
        "views/stock_barcodes_action_view.xml",
        "views/stock_barcodes_option_view.xml",
        "views/stock_inventory_views.xml",
        "views/stock_location_views.xml",
        "views/stock_picking_views.xml",
        "wizard/stock_production_lot_views.xml",
        "wizard/stock_barcodes_read_views.xml",
        "wizard/stock_barcodes_read_inventory_views.xml",
        "wizard/stock_barcodes_read_picking_views.xml",
        "wizard/stock_barcodes_read_todo_view.xml",
        # Keep order
        "views/stock_barcodes_menu.xml",
    ],
    "installable": True,
    "pre_init_hook": "pre_init_hook",
}
