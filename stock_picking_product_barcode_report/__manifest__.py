# Copyright 2020 Carlos Roca <carlos.roca@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Stock Picking Product Barcode Report",
    "summary": "It provides a wizard to select how many barcodes print.",
    "version": "13.0.2.2.0",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-barcode",
    "license": "AGPL-3",
    "maintainers": ["CarlosRoca13"],
    "category": "Extra Tools",
    "depends": ["stock"],
    "external_dependencies": {"python": ["python-barcode"]},
    "data": [
        "views/res_config_settings_view.xml",
        "data/paperformat_label.xml",
        "wizard/stock_barcode_selection_printing_view.xml",
        "report/report_label_barcode.xml",
        "report/report_label_barcode_quant_package_template.xml",
        "report/report_label_barcode_template.xml",
        "data/ir_actions_report_data.xml",
        "views/ir_actions_report_view.xml",
    ],
    "installable": True,
}
