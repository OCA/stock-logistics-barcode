# Copyright 2019 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Stock Barcodes",
    "summary": "It provides read barcode on stock operations.",
    "version": "16.0.2.0.0",
    "author": "Tecnativa, " "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-barcode",
    "license": "AGPL-3",
    "category": "Extra Tools",
    "depends": ["barcodes", "stock", "web_widget_numeric_step", "web", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "views/stock_barcodes_action_view.xml",
        "views/stock_barcodes_option_view.xml",
        "views/stock_location_views.xml",
        "views/stock_picking_views.xml",
        "wizard/stock_production_lot_views.xml",
        "wizard/stock_barcodes_read_views.xml",
        "wizard/stock_barcodes_read_picking_views.xml",
        "wizard/stock_barcodes_read_todo_view.xml",
        "wizard/stock_barcodes_read_inventory_views.xml",
        # Keep order
        "data/stock_barcodes_action.xml",
        "data/stock_barcodes_option.xml",
        "views/stock_barcodes_menu.xml",
        # Reports
        "reports/barcode_actions_report.xml",
        "reports/reports.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "/stock_barcodes/static/src/**/*.esm.js",
            (
                "after",
                "/web_widget_numeric_step/static/src/numeric_step.xml",
                "/stock_barcodes/static/src/widgets/numeric_step.xml",
            ),
            "/stock_barcodes/static/src/views/kanban/stock_barcodes_kanban.xml",
            "/stock_barcodes/static/src/widgets/view_button.xml",
            "/stock_barcodes/static/src/views/actions/stock_barcode_main_menu.xml",
            "/stock_barcodes/static/src/**/*.scss",
        ],
    },
    "installable": True,
    "pre_init_hook": "pre_init_hook",
}
