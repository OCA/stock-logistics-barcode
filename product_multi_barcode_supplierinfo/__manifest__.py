# Copyright 2022 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Multi barcode from supplier pricelist",
    "summary": "Adds  supplier pricelist barcode in product barcode",
    "version": "16.0.1.0.0",
    "category": "Product Management",
    "website": "https://github.com/OCA/stock-logistics-barcode",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["product_supplierinfo_barcode", "product_multi_barcode"],
    "installable": True,
    "auto_install": True,
    "data": [
        "views/product_template_view.xml",
    ],
    "pre_init_hook": "copy_barcode",
    "post_init_hook": "update_barcodes_ids",
}
