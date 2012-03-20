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
    "name" : "Stock bar code reader",
    "version" : "1.0",
    "author" : "Julius Network Solutions",
    "description" : """ This module is an ergonomic wizard to fill in package """,
    "website" : "http://www.julius.fr",
    "depends" : [
         "stock",
         "stock_tracking_extended",
         "stock_tracking_add_move",
    ],
    "category" : "Customs/Stock",
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [
        'wizard/reference_view.xml',
        'acquisition_view.xml',
        'stock_view.xml',
        'data/acquisition_sequence.xml',
        "security/ir.model.access.csv",
    ],
    'test': [],
    'installable': True,
    'active': False,
    'certificate': '',
}
