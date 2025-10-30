# Copyright 2025 Binhex <https://www.binhex.cloud>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Stock Barcodes Quality Control",
    "summary": """Allows quality control to be integrated with barcode scanning.""",
    "version": "17.0.1.0.0",
    "license": "AGPL-3",
    "author": "Edilio Escalona Almira - Binhexteam,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-barcode",
    "depends": ["stock_barcodes", "quality_control_stock_oca"],
    "data": [
        "security/ir.model.access.csv",
        "data/stock_barcodes_action_data.xml",
        "views/stock_barcodes_option_views.xml",
        "wizard/quality_control_validate_wizard_views.xml",
        "wizard/stock_barcodes_read_picking_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "/stock_barcodes_quality_control/static/src/**/*.esm.js",
            "/stock_barcodes_quality_control/static/src/**/*.xml",
            "/stock_barcodes_quality_control/static/src/**/*.scss",
        ],
    },
    "auto_install": True,
}
