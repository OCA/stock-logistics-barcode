# Copyright 2024 Akretion France (https://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class WizStockBarcodesRead(models.AbstractModel):
    _inherit = "wiz.stock.barcodes.read"

    expiry_date = fields.Date(readonly=True)

    def _process_ai_17(self, gs1_list):
        self.expiry_date = self.barcode
        return True

    def _prepare_lot_vals(self):
        vals = super()._prepare_lot_vals()
        if self.expiry_date:
            vals["expiry_date"] = self.expiry_date
        return vals

    def action_clean_lot(self):
        self.expiry_date = False
        return super().action_clean_lot()
