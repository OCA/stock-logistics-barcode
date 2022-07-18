import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo11-addons-oca-stock-logistics-barcode",
    description="Meta package for oca-stock-logistics-barcode Odoo addons",
    version=version,
    install_requires=[
        'odoo11-addon-barcodes_generator_abstract',
        'odoo11-addon-barcodes_generator_lot',
        'odoo11-addon-barcodes_generator_partner',
        'odoo11-addon-barcodes_generator_picking',
        'odoo11-addon-barcodes_generator_product',
        'odoo11-addon-base_gs1_barcode',
        'odoo11-addon-mobile_app_abstract',
        'odoo11-addon-mobile_app_angular',
        'odoo11-addon-mobile_app_picking',
        'odoo11-addon-product_multi_ean',
        'odoo11-addon-stock_barcodes',
        'odoo11-addon-stock_barcodes_gs1',
        'odoo11-addon-stock_barcodes_gs1_expiry',
        'odoo11-addon-stock_barcodes_move_location',
        'odoo11-addon-stock_scanner',
        'odoo11-addon-stock_scanner_inventory',
        'odoo11-addon-stock_scanner_location_info',
        'odoo11-addon-stock_scanner_receipt',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 11.0',
    ]
)
