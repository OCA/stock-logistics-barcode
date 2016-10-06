# -*- coding: utf-8 -*-
##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2004-TODAY Tech-Receptives(<http://www.tech-receptives.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'TR Barcode',
    'version': '1.1.4',
    'category': 'Warehouse Management',
    'description': """

Presentation:

This module adds the menu Barcode used to generate and configuration barcodes.

    """,
    'author': "Tech-Receptives Solutions Pvt. Ltd.,Odoo Community Association (OCA)",
    'website': 'http://www.techreceptives.com',
    'license': 'AGPL-3',
    'depends': [
        "base",
        'stock',
    ],
    'data': [
        "wizard/tr_barcode_wizard.xml",
        "res_config_view.xml",
        "tr_barcode_view.xml",
        "security/ir.model.access.csv",
    ],
    'demo': [],
    'test': [],
    'installable': False,
    'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
