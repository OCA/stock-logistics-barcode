# -*- encoding: utf-8 -*-
##############################################################################
#
#    This module is copyright (C) 2009 Numérigraphe SARL. All Rights Reserved.
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
"""This file customizes the "Users" object"""

from osv import osv, fields

# XXX This would probably be best in res_config_users
class res_users(osv.osv):
    """Add the bar code decoding configuration to the user profile"""
    _inherit = 'res.users'

    _columns = {
        # XXX those should be properties, not standard fields
        'gs1_128_prefix': fields.char('GS1-128 Prefix', size=64,help="The prefix that the barcode scanner will send when GS1-128 codes are scanned. No prefix is expected if this fields is left empty"),
        'gs1_128_separator': fields.char('GS1-128 Group Separator', size=1,
                                         help="The characters that the barcode scanner will send when a <GS> (Group Separator) is encountered in a GS1-128 code. <GS> is usually found when the data is of variable length. The ASCII character 29 will be used as a default if this field is left empty."),
    }
res_users()
