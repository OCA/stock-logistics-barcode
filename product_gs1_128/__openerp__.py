# -*- encoding: utf-8 -*-
##############################################################################
#
#    This module is copyright (C) 2010 Numérigraphe SARL. All Rights Reserved.
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
    'name' : 'Decoding features for GS1-128 codes (aka UCC/EAN-128)',
    'version' : '0.1',
    'author' : u'Numérigraphe',
    'website': 'http://numerigraphe.com',
    'category': 'Generic Modules/Inventory Control',
    'description': """
This makes OpenERP capable of decoding GS1-128 codes.

GS1-128 (formerly known as UCC-128, EAN 128 or UCC/EAN-128) is a standard for \
encoding item identification and logistics data.
Physically it is represented as a Code-128 barcode, but this module does not \
directly allow you to print or scan them.

Instead, the focus of this module is on decoding the data contained in \
barcodes. To this end, it provides objects to fine-tune the Application Identifiers and
the associated data types.
""",
    'depends' : [
        'product',
    ],
    'init_xml' : [],
    'update_xml' : [
        'product_gs1_128_view.xml',
        'res_users_view.xml',
        'data/product.gs1_128.csv',
        "security/ir.model.access.csv",
    ],
    'active': False,
    'installable': True,
    'license' : 'GPL-3',
}
