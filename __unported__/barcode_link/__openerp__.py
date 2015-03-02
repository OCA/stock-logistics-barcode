# -*- coding: utf-8 -*-
#################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 Julius Network Solutions SARL <contact@julius.fr>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#################################################################################

{
    "name": "Barcode link Module",
    "version": "1.0",
    "author": "Julius Network Solutions,Odoo Community Association (OCA)",
    "description": """

Presentation:

The module Barcode_link adds a field Link in the barcode form.
And link the barcode with a product.

""",
    "website": "http://www.julius.fr",
    "license": "GPL-3 or any later version",
    "depends": [
        "tr_barcode",
    ],
    "category": "Generic Modules/Inventory Control",
    "demo": [],
    "data": [
        'barcode_link_view.xml',
    ],
    'test': [],
    'installable': False,
    'active': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
