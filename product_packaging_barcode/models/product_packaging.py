# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductPackaging(models.Model):

    _inherit = 'product.packaging'

    barcode = fields.Char(
        copy=False,
        help="Barcode used for packaging identification.",
    )
