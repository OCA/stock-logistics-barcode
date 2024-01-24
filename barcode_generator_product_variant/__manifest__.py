{
    "name": "Barcode Generator Product Variant",
    "version": "14.0.1.0.1",
    "depends": ["barcodes_generator_product"],
    "author": "PyTech SRL, Ooops404, Odoo Community Association (OCA)",
    "maintainers": ["aleuffre", "renda-dev", "PicchiSeba"],
    "website": "https://github.com/OCA/stock-logistics-barcode",
    "category": "Tools",
    "license": "AGPL-3",
    "data": [
        "security/ir.model.access.csv",
        "views/product_template_views.xml",
        "wizards/product_product_barcode_wizard_views.xml",
    ],
    "demo": [
        "demo/barcode_rule_demo.xml",
    ],
    "installable": True,
    "application": False,
}
