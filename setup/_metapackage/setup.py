import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo13-addons-oca-stock-logistics-barcode",
    description="Meta package for oca-stock-logistics-barcode Odoo addons",
    version=version,
    install_requires=[
        'odoo13-addon-base_gs1_barcode',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
