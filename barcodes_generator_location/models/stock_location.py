# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class StockLocation(models.Model):
    _name = 'stock.location'
    _description = 'Stock Location'
    _inherit = ['stock.location', 'barcode.generate.mixin']
