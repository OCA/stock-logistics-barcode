# Copyright 2019 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Stock Barcodes JSON",
    "summary": "It provides read JSON barcode on stock operations.",
    "version": "13.0.1.0.0",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "website": "https://odoo-community.org/",
    "license": "AGPL-3",
    "category": "Extra Tools",
    "depends": ["stock_barcodes", "printer_zpl2"],
    "data": [
        "views/barcode_views.xml",
        "security/ir.model.access.csv",
        "wizard/print_record_label.xml",
    ],
    "installable": True,
}
