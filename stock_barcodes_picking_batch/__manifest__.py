# Copyright 2021 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Stock Barcodes Picking Batch",
    "summary": "It provides read barcodes on stock operations from batch pickings.",
    "version": "13.0.1.0.0",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-barcode",
    "license": "AGPL-3",
    "category": "Extra Tools",
    "depends": ["stock_barcodes", "stock_picking_batch_extended"],
    "data": [
        "data/stock_barcodes_action.xml",
        "views/assets.xml",
        "views/stock_picking_batch_views.xml",
        "wizard/stock_barcodes_read_picking_batch_views.xml",
    ],
    "installable": True,
    "auto_install": True,
}
