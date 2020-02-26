# Copyright 2020 ForgeFlow S.L. (<http://www.forgeflow.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Stock Barcodes ZPL II",
    "summary": "It provides zpl barcodes support for several stock models.",
    "version": "13.0.1.0.0",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-barcode",
    "license": "AGPL-3",
    "category": "Extra Tools",
    "depends": ["stock_barcodes", "printer_zpl2"],
    "data": ["data/actions.xml", "wizard/print_record_label.xml"],
    "installable": True,
}
