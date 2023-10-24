# Copyright 2019 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import datetime

from odoo import fields, models


class WizStockBarcodesRead(models.AbstractModel):
    _inherit = "wiz.stock.barcodes.read"

    expiration_date = fields.Datetime(
        string="End of Life Date",
    )
    use_date = fields.Datetime(
        string="Best before Date",
    )

    def _process_ai_15(self, gs1_list):
        """Preferred date identification"""
        self.use_date = self.barcode
        return True

    def _process_ai_17(self, gs1_list):
        """expiration date identification"""
        self.expiration_date = self.barcode
        return True

    def _prepare_lot_vals(self):
        vals = super()._prepare_lot_vals()
        # Try set expiration date from ai 17 (expiration_date), if not, set from ai 15
        if self.expiration_date:
            vals["expiration_date"] = self.expiration_date
            if not self.use_date:
                vals["use_date"] = self.expiration_date - datetime.timedelta(
                    days=self.product_id.use_time
                )
        if self.use_date:
            vals["use_date"] = self.use_date
            if not self.expiration_date:
                vals["expiration_date"] = self.use_date + datetime.timedelta(
                    days=self.product_id.use_time
                )
        expiration_date = vals.get("expiration_date")
        if expiration_date:
            vals.update(
                {
                    "removal_date": expiration_date
                    - datetime.timedelta(days=self.product_id.removal_time),
                    "alert_date": expiration_date
                    - datetime.timedelta(days=self.product_id.alert_time),
                }
            )
        return vals

    def action_clean_lot(self):
        self.expiration_date = False
        self.use_date = False
        return super().action_clean_lot()
