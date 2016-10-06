# -*- coding: utf-8 -*-
#################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 Julius Network Solutions SARL <contact@julius.fr>
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
    "name": "Barcode for production lots",
    "version": "1.1",
    "author": "Julius Network Solutions,Odoo Community Association (OCA)",
    "website": "http://www.julius.fr",
    "license": "GPL-3 or any later version",
    "category": "Warehouse Management",
    "depends": [
        "stock",
        "tr_barcode_config",
        "tr_barcode_field",
    ],
    "description": """
This module provides a stock.production.lot model deriving from barcode_osv,
which will manage the population of the x_barcode_id column.

It is still necessary to configure the model to specify which field is used to
generate the barcode.
     """,
    "demo": [],
    "data": [
        'data/model_data.xml',
        'data/config_data.xml',
        'res_config_view.xml',
    ],
    "active": False,
    'installable': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
