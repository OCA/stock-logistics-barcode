# -*- coding: utf-8 -*-
##############################################################################
#
#    This module is copyright (C) 2012-2014 Numérigraphe SARL.
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
    'name': 'Decoding API for GS1-128 (aka UCC/EAN-128) and GS1-Datamatrix',
    'version': '1.0',
    'author': u'Numérigraphe',
    'website': 'http://numerigraphe.com',
    'category': 'Hidden',
    'description': """
API for decoding the content of structured barcodes GS1-128/Datamatrix
======================================================================

GS1-128 (formerly known as UCC-128, EAN 128 or UCC/EAN-128), and GS1-Datamatrix
are standards for encoding item identification and logistics data.
Physically, GS1-128 is represented as a 1-dimension Code-128 barcode and
GS1-Datamtrix is represented as a 2-dimensions Datamatrix barcode.

When those barcodes are read, their content can be decode into multiple values
using a set of standard "Application Identifiers". For example, most pharmacy
items have a GS1-Datamatrix barcode containg their GTIN, lot number and
expiry date.

This module does not directly allow you to print or scan barcodes.
Instead, the focus of this module is on decoding the data contained in
barcodes. To this end, it provides objects to fine-tune the Application
Identifiers and the associated data types.

Caveat Emptor: when an "Application Identifiers" has variable-length data,
the barcodes must contain a special character (<GS>, group separator)
but as this is not an ASCII character. Some barcdode readers will not include
this character: decoding the structured data will then be impossible. Other
readers will translate GS1 to ASCII character 29, but this character is not
printable, and some applications may not record it. Yet other readers will
let you configure how to map <GS>, which may help improve compatibility.
""",
    'depends': [
        'product',
    ],
    'data': [
        'gs1_barcode_view.xml',
        'res_users_view.xml',
        'data/gs1_barcode.csv',
        "security/ir.model.access.csv",
    ],
    'test': [
        'test/gs1_barcode_test.yml'
    ],
    'installable': True,
    'license': 'AGPL-3',
}
