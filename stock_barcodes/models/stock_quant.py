# Copyright 2023 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    def action_barcode_inventory_quant_unlink(self):
        for quant in self:
            # quant.with_context(inventory_mode=True).unlink()
            quant.with_context(inventory_mode=True).inventory_quantity = 0.0
