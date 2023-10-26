# Copyright 2023 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Product Multi Barcode Constraint per Company",
    "version": "14.0.1.0.0",
    "category": "Product",
    "summary": """This is a bridge module between "product_multi_barcode" and
    "product_barcode_constraint_per_company" """,
    "author": "Cetmix, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-barcode",
    "maintainers": ["dessanhemrayev", "CetmixGitDrone"],
    "license": "AGPL-3",
    "depends": [
        "product_multi_barcode",
        "product_barcode_constraint_per_company",
    ],
    "installable": True,
    "auto_install": True,
}
