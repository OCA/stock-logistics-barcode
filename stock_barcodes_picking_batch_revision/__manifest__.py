# Copyright 2023 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Stock Barcodes Picking Batch Revision",
    "summary": "It provides batch pickings revision from other users.",
    "version": "15.0.1.0.0",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-barcode",
    "license": "AGPL-3",
    "category": "Extra Tools",
    "depends": ["stock_barcodes_picking_batch"],
    "data": [
        "data/stock_barcodes_action.xml",
        "views/stock_picking_batch_views.xml",
        "wizard/stock_barcodes_read_picking_batch_views.xml",
    ],
    "installable": True,
    "assets": {
        "web.assets_backend": [
            "stock_barcodes_picking_batch_revision/static/src/js/boolean_toggle_big.js",
            "stock_barcodes_picking_batch_revision/static/src/scss/boolean_toggle_big.scss",
        ],
    },
}
