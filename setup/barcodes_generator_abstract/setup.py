import setuptools

setuptools.setup(
    setup_requires=['setuptools-odoo'],
    odoo_addon={
        'external_dependencies_override': {
            'python': {
                'barcode': 'python-barcode == 0.12.0',
            },
        },
    },
)
