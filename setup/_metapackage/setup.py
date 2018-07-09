import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo11-addons-oca-stock-logistics-barcode",
    description="Meta package for oca-stock-logistics-barcode Odoo addons",
    version=version,
    install_requires=[
        'odoo11-addon-barcodes_generator_abstract',
        'odoo11-addon-barcodes_generator_product',
        'odoo11-addon-stock_scanner',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
