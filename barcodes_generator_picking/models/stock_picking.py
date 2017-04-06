# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockPicking(models.Model):
    _name = 'stock.picking'
    _description = 'Stock Picking'
    _inherit = ['stock.picking', 'barcode.generate.mixin']

    barcode = fields.Char()
