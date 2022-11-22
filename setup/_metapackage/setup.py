import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-oca-stock-logistics-barcode",
    description="Meta package for oca-stock-logistics-barcode Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-base_gs1_barcode>=15.0dev,<15.1dev',
        'odoo-addon-product_supplierinfo_barcode>=15.0dev,<15.1dev',
        'odoo-addon-stock_picking_product_barcode_report>=15.0dev,<15.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 15.0',
    ]
)
