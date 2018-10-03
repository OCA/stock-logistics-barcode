import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo10-addons-oca-stock-logistics-barcode",
    description="Meta package for oca-stock-logistics-barcode Odoo addons",
    version=version,
    install_requires=[
        'odoo10-addon-barcodes_ean14',
        'odoo10-addon-barcodes_generator_abstract',
        'odoo10-addon-barcodes_generator_location',
        'odoo10-addon-barcodes_generator_lot',
        'odoo10-addon-barcodes_generator_package',
        'odoo10-addon-barcodes_generator_partner',
        'odoo10-addon-barcodes_generator_picking',
        'odoo10-addon-barcodes_generator_product',
        'odoo10-addon-stock_scanner',
        'odoo10-addon-stock_scanner_inventory',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
