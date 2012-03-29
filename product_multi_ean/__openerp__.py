# -*- encoding: utf-8 -*-
##############################################################################
#
#    Author Guewen Baconnier. Copyright Camptocamp SA
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
##############################################################################

{
    'name' : 'Multiple EAN13 on products',
    'version' : '1.0',
    'depends' : ['base', 'product'],
    'author' : 'Camptocamp',
    'description': """Multiple EAN13 for one product.
Product EAN13 field is replaced by a function which returns the first EAN13 found.

Need to manually comment out the constraint :
_constraints = [(_check_ean_key, 'Error: Invalid ean code', ['ean13'])]
in product/product.py because, sadly, it is impossible to inherit it.

WARNING !!! THIS WILL DROP ALL YOUR CURRENT EAN13 AS OPENERP DROP THE COLUMN.
PLEASE BE SURE TO EXPORT THEM BEFORE INSTALLATION OF THE MODULE AND RESTORE THEM WITH AN IMPORT.

""",
    'website': 'http://www.camptocamp.com',
    'init_xml': [],
    'update_xml': ['product_view.xml',
                   'security/ir.model.access.csv'],
    'demo_xml': [],
    'installable': True,
    'active': False,
}
