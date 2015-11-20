# -*- coding: utf-8 -*-
##############################################################################
#
#    Author:  Author Guewen Baconnier
#    Copyright 2012-2014 Camptocamp SA
#    Author:  Roberto Lizana
#    Copyright 2015 Trey, Kilobytes de Soluciones
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
    'name': 'Multiple EAN13 on products',
    'version': '1.3',
    'license': 'AGPL-3',
    'author': "Camptocamp,"
              "Trey,"
              "Odoo Community Association (OCA)",
    'category': 'Warehouse',
    'depends': ['product'],
    'website': 'https://github.com/OCA/stock-logistics-barcode',
    'data': [
        'views/product_view.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
}
