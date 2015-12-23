# -*- coding: utf-8 -*-
##############################################################################
#
#    Stock Inventory Barcode module for Odoo
#    Copyright (C) 2015 Akretion (http://www.akretion.com)
#    @author Alexis de Lattre <alexis.delattre@akretion.com>
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
    'name': "Barcode Input for Inventories",
    'version': "8.0.0.1.0",
    'category': "Inventory, Logistic, Storage",
    'author': 'Akretion,Odoo Community Association (OCA)',
    'summary': "Add simple barcode interface on inventories",
    'license': 'AGPL-3',
    "description": """This module adds input fields to the inventory view
which allow to add products to the inventory list by a barcode scanner.
For this the barcode scanner must be configured as a keyboard that appends
a LF after the scan and the cursor must be in the barcode field.

The barcode input functionality is provided by a abstract model that can also
be used with other models.
""",
    'depends': ['stock'],
    'data': [
        'wizard/stock_inventory_barcode_view.xml',
        'stock_view.xml',
        ],
    'installable': True,
}
