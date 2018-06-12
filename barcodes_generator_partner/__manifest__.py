# Copyright (C) 2014-Today GRAP (http://www.grap.coop)
# Copyright (C) 2016-Today La Louve (http://www.lalouve.net)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Generate Barcodes for Partners',
    'summary': 'Generate Barcodes for Partners',
    'version': '11.0.1.0.0',
    'category': 'Tools',
    'author':
        'GRAP,'
        'La Louve,'
        'Odoo Community Association (OCA)',
    'website': 'https://www.odoo-community.org',
    'license': 'AGPL-3',
    'depends': [
        'barcodes_generator_abstract',
        'point_of_sale',
    ],
    'data': [
        'views/view_res_partner.xml',
    ],
    'demo': [
        'demo/ir_sequence.xml',
        'demo/barcode_rule.xml',
        'demo/res_partner.xml',
        'demo/function.xml',
    ],
}
