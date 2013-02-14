# -*- coding: utf-8 -*-
##############################################################################
#
#    Author:  Author Guewen Baconnier
#    Copyright 2012 Camptocamp SA
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

{'name' : 'Multiple EAN13 on products',
 'version' : '1.1',
 'author' : 'Camptocamp',
 'maintainer': 'Camptocamp',
 'category': 'Warehouse',
 'complexity': "normal",  # easy, normal, expert
 'depends' : ['base', 'product'],
 'description': """"
Allow Multiple EAN13 on products.
A list of EAN13 is available for each product with a priority, so a
main ean13 code is defined.
""",
 'website': 'http://www.camptocamp.com',
 'init_xml': [],
 'update_xml': [
                'product_view.xml',
                'security/ir.model.access.csv'],
 'demo_xml': [],
 'tests': [],
 'installable': False,
 'images' : ['/static/src/images/image'],
 'auto_install': False,
 'license': 'AGPL-3',
 'application': True
}
