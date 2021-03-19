# Copyright 2021 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Stock Picking Product Barcode Report Quant",
    "summary": """It provides a wizard to select how many
        barcodes print based on quants.""",
    "version": "13.0.1.0.0",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "website": "https://odoo-community.org/",
    "license": "AGPL-3",
    "maintainers": ["sergio-teruel"],
    "category": "Extra Tools",
    "depends": ["stock_picking_product_barcode_report", "stock_quant_barcode"],
    "data": [
        "data/paperformat.xml",
        "report/report_label_barcode.xml",
        "report/report_label_barcode_quant.xml",
        "report/report_label_barcode_template.xml",
        "report/report_label_barcode_template_quant.xml",
        "wizard/stock_barcode_selection_printing_view.xml",
    ],
    "installable": True,
}
