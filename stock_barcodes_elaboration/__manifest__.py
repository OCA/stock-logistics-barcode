# Copyright 2023 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Stock Barcodes Elaboration",
    "summary": "Extends barcode reader module to show elaboration info"
    "into secondary unit data.",
    "version": "15.0.1.1.0",
    "author": "Tecnativa, " "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-barcode",
    "license": "AGPL-3",
    "category": "Extra Tools",
    "depends": ["stock_barcodes", "sale_elaboration"],
    "data": [
        "wizard/stock_barcodes_read_picking_views.xml",
        "wizard/stock_barcodes_read_todo_view.xml",
    ],
    "installable": True,
    "auto_install": True,
    "assets": {
        "web.assets_backend": [
            "/stock_barcodes_elaboration/static/src/css/stock_barcodes_elaboration.scss",
        ],
    },
}
