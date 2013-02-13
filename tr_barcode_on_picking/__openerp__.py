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
    "name" : "Barcode for pickings",
    "version" : "1.0",
    "author" : "Julius Network Solutions",
    "website" : "http://www.julius.fr",
    "category" : "Customs/Stock",
    "depends" : [
        "stock",
        "tr_barcode_config",
        "tr_barcode_field",
    ],
    "description" : """This module provides a stock.picking model deriving from barcode_osv, which will manage the population of the x_barcode_id column. 

It is still necessary to configure the model to specify which field is used to generate the barcode.
     """,
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [],
    "active": False,
    "installable": False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
