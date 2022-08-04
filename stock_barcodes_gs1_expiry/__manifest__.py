# Copyright 2019 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Stock Barcodes GS1 Expiry",
    "summary": "It provides read expiry dates from GS1 barcode on " "stock operations.",
    "version": "13.0.1.0.1",
    "author": "Tecnativa, " "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-barcode",
    "license": "AGPL-3",
    "category": "Extra Tools",
    "depends": ["stock_barcodes_gs1", "product_expiry"],
    "data": ["wizard/stock_production_lot_views.xml"],
    "installable": True,
    "auto_install": True,
}
