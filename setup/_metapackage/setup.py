import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo8-addons-oca-stock-logistics-barcode",
    description="Meta package for oca-stock-logistics-barcode Odoo addons",
    version=version,
    install_requires=[
        'odoo8-addon-base_gs1_barcode',
        'odoo8-addon-product_barcode_generator',
        'odoo8-addon-product_multi_ean',
        'odoo8-addon-stock_disable_barcode_interface',
        'odoo8-addon-stock_inventory_barcode',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
