# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    'name': 'Stock Picking Barcode',
    'version': '12.0.1.0.0',
    'author': 'Eficent',
    'category': 'Warehouse Management',
    'depends': [
        'stock',
        'barcodes',
        'web_ir_actions_act_view_reload',
    ],
    'data': [
        'wizard/wizard_stock_picking_barcode_views.xml',
        'views/stock_picking_views.xml',
    ],
    'website': 'https://github.com/OCA/stock-logistics-barcode',
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
}
