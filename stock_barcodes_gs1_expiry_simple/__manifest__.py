# Copyright 2024 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Stock Barcodes GS1 Expiry Simple",
    "version": "16.0.1.0.0",
    "category": "Warehouse",
    "license": "AGPL-3",
    "summary": "Glue module between stock_barcodes_gs1 and product_expiry_simple",
    "author": "Akretion,Odoo Community Association (OCA)",
    "maintainers": ["alexis-via"],
    "development_status": "Mature",
    "website": "https://github.com/OCA/stock-logistics-barcode",
    "depends": ["stock_barcodes_gs1", "product_expiry_simple"],
    "data": [
        "wizards/stock_barcodes_read_view.xml",
    ],
    "installable": True,
    "auto_install": True,
}
