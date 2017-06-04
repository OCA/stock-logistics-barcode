# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 initOS GmbH & Co. KG (<http://www.initos.com>).
#    Author Katja Matthes <katja.matthes at initos.com>
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
    "name": "Barcode Input for Inventories",
    "version": "0.1",
    "depends": [
        'stock',
    ],
    'author': 'initOS GmbH & Co. KG',
    "category": "Stock",
    "summary": "",
    'license': 'AGPL-3',
    "description": """This module adds input fields to the inventory view
which allow to add products to the inventory list by a barcode scanner.
For this the barcode scanner must be configured as a keyboard that appends
a LF after the scan and the cursor must be in the barcode field.

The barcode input functionality is provided by a abstract model that can also
be used with other models.
""",
    'data': [
        'stock_view.xml',
    ],
    'demo': [
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
}
