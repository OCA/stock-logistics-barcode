# Copyright 2012-2014 Numérigraphe SARL.
from odoo import fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    gs1_barcode_prefix = fields.Char(
        "Prefix",
        help=(
            "The prefix that the barcode scanner will send when GS1-128 "
            "or GS1-Datamatrix codes are scanned. No prefix is expected "
            "if this fields is left empty"
        ),
    )
    gs1_barcode_separator = fields.Char(
        "Group Separator",
        size=1,
        help=(
            "The characters that the barcode scanner will send when a "
            "<GS> (Group Separator) is encountered in a GS1-128 or "
            "GS1-Datamatrix code. <GS> is usually found when the data is of "
            "variable length. The ASCII character 29 will be expected by "
            "default if this field is left empty."
        ),
    )
