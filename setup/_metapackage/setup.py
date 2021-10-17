import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo9-addons-oca-stock-logistics-barcode",
    description="Meta package for oca-stock-logistics-barcode Odoo addons",
    version=version,
    install_requires=[
        'odoo9-addon-barcodes_generator_abstract',
        'odoo9-addon-barcodes_generator_partner',
        'odoo9-addon-barcodes_generator_product',
        'odoo9-addon-stock_scanner',
        'odoo9-addon-stock_scanner_inventory',
        'odoo9-addon-stock_scanner_location_info',
        'odoo9-addon-stock_scanner_receipt',
        'odoo9-addon-stock_scanner_shipping',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 9.0',
    ]
)
