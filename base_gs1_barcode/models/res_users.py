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

from openerp import models, fields


class ResUsers(models.Model):
    _inherit = 'res.users'

    gs1_barcode_prefix = fields.Char(
        'Prefix',
        help=("The prefix that the barcode scanner will send when GS1-128 "
              "or GS1-Datamatrix codes are scanned. No prefix is expected "
              "if this fields is left empty"))
    gs1_barcode_separator = fields.Char(
        'Group Separator',
        size=1,
        help=("The characters that the barcode scanner will send when a "
              "<GS> (Group Separator) is encountered in a GS1-128 or "
              "GS1-Datamatrix code. <GS> is usually found when the data is of "
              "variable length. The ASCII character 29 will be expected by "
              "default if this field is left empty."))
