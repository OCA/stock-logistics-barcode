# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Stock Barcodes GS1 Net Weight",
    "summary": "Reading the AI 3100 form a GS1 Barcode in case of variable weight used instead of quantity.",
    "version": "13.0.1.0.0",
    "author": "ITuAS GmbH",
    "website": "https://ituas.at/",
    "license": "AGPL-3",
    "category": "Extra Tools",
    "depends": ["stock_barcodes_gs1", "product_expiry"],
    "data": ["wizard/stock_production_lot_views.xml"],
    "installable": True,
    "auto_install": True,
}
