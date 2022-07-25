# Copyright 2022 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class StockProductionLot(models.Model):
    _inherit = "stock.production.lot"

    # Increase performance in scan barcode operations
    name = fields.Char(index=True)
    product_id = fields.Many2one(index=True)
