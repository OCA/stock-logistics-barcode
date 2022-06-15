# Copyright 2019 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Stock Barcodes GS1 Secondary Unit",
    "summary": "It provides read package from GS1 barcode stored "
    "into secondary unit data.",
    "version": "13.0.1.0.0",
    "author": "Tecnativa, " "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-barcode",
    "license": "AGPL-3",
    "category": "Extra Tools",
    "depends": ["stock_barcodes_gs1", "stock_secondary_unit"],
    "data": [
        "views/product_views.xml",
        "wizard/stock_barcodes_read_inventory_views.xml",
        "wizard/stock_barcodes_read_picking_views.xml",
    ],
    "installable": True,
    "auto_install": True,
}
