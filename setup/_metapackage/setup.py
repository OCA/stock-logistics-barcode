import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo12-addons-oca-stock-logistics-barcode",
    description="Meta package for oca-stock-logistics-barcode Odoo addons",
    version=version,
    install_requires=[
        'odoo12-addon-barcodes_generator_abstract',
        'odoo12-addon-barcodes_generator_product',
        'odoo12-addon-product_multi_ean',
        'odoo12-addon-stock_scanner',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
