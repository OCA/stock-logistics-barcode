# -*- coding: utf-8 -*-
# Copyright 2012 Numérigraphe SARL. All Rights Reserved.
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl).

from odoo import models, fields


# XXX This would probably be best in res_config_users
class ResUsers(models.Model):
    """Add the bar code decoding configuration to the user profile"""
    _inherit = 'res.users'

    gs1_barcode_prefix = fields.Char(
        string='Prefix',
        size=64,
        help="The prefix that the barcode scanner will send when GS1-128 "
             "or GS1-Datamatrix codes are scanned. No prefix is expected "
             "if this fields is left empty"
    )
    gs1_barcode_separator = fields.Char(
        string='Group Separator',
        size=1,
        help="The characters that the barcode scanner will send when a "
             "<GS> (Group Separator) is encountered in a GS1-128 or "
             "GS1-Datamatrix code. <GS> is usually found when the data "
             "is of variable length. The ASCII character 29 will be "
             "expected by default if this field is left empty."
    )
