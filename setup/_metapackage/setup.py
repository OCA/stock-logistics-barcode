import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo13-addons-oca-stock-logistics-barcode",
    description="Meta package for oca-stock-logistics-barcode Odoo addons",
    version=version,
    install_requires=[
        'odoo13-addon-base_gs1_barcode',
        'odoo13-addon-stock_barcodes',
        'odoo13-addon-stock_barcodes_automatic_entry',
        'odoo13-addon-stock_barcodes_gs1',
        'odoo13-addon-stock_barcodes_move_location',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
