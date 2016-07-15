# -*- coding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Julius Network Solutions SARL <contact@julius.fr>
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
###############################################################################

{
    "name": 'Product barcode generator',
    "license": "AGPL-3",
    "category": "Stock Management",
    "version": '9.0.1.0.0',
    "author": 'IT-Projects LLC, Julius Network Solutions, Odoo Community Association (OCA)',
    "website": 'http://www.julius.fr/',
    "depends": [
        'product',
    ],
    "demo": [],
    "data": [
        "data/ean_sequence.xml",
        "views/res_company_view.xml",
        "views/product_view.xml",
        "views/sequence_view.xml",
    ],
    'installable': True,
    "active": False,
}
