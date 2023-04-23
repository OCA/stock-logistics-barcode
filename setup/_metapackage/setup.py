import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo13-addons-oca-stock-logistics-barcode",
    description="Meta package for oca-stock-logistics-barcode Odoo addons",
    version=version,
    install_requires=[
        'odoo13-addon-barcodes_generator_abstract',
        'odoo13-addon-barcodes_generator_location',
        'odoo13-addon-barcodes_generator_product',
        'odoo13-addon-base_gs1_barcode',
        'odoo13-addon-product_gs1_barcode',
        'odoo13-addon-product_gtin',
        'odoo13-addon-product_multi_barcode',
        'odoo13-addon-stock_barcodes',
        'odoo13-addon-stock_barcodes_automatic_entry',
        'odoo13-addon-stock_barcodes_gs1',
        'odoo13-addon-stock_barcodes_gs1_expiry',
        'odoo13-addon-stock_barcodes_move_location',
        'odoo13-addon-stock_barcodes_picking_batch',
        'odoo13-addon-stock_picking_product_barcode_report',
        'odoo13-addon-stock_picking_product_barcode_report_secondary_unit',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 13.0',
    ]
)
