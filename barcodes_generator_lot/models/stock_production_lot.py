# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockProductionLot(models.Model):
    _name = 'stock.production.lot'
    _description = 'Stock Production Lot'
    _inherit = ['stock.production.lot', 'barcode.generate.mixin']

    barcode = fields.Char(
        related='name',
    )
