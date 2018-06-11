# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProductPackaging(models.Model):
    _name = 'product.packaging'
    _description = 'Product Packaging'
    _inherit = ['product.packaging', 'barcode.generate.mixin']

    barcode = fields.Char()
