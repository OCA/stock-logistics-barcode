# Copyright 2023 Akretion (https://www.akretion.com).
# @author Pierrick Brun <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Product Multi Barcode Constraint per Company",
    "version": "16.0.1.0.1",
    "category": "Product",
    "summary": "Glue module for product_multi_barcode and"
    "product_barcode_constraint_per_company",
    "author": "akretion, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-barcode",
    "license": "AGPL-3",
    "depends": [
        "product_multi_barcode",
        "product_barcode_constraint_per_company",
    ],
    "data": ["security/ir_rule.xml"],
    "installable": True,
    "auto_install": True,
}
