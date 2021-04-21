# Copyright 2019 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models


class StockInventory(models.Model):
    _inherit = ["barcodes.barcode_events_mixin", "stock.inventory"]
    _name = "stock.inventory"

    def action_barcode_scan(self):
        self.start_empty = True
        self._action_start()
        self._check_company()
        vals = {
            "inventory_id": self.id,
            "res_model_id": self.env.ref("stock.model_stock_inventory").id,
            "res_id": self.id,
            "location_id": self.location_ids[:1].id,
            "product_id": self.product_ids[:1].id,
        }
        wiz = self.env["wiz.stock.barcodes.read.inventory"].create(vals)
        action = wiz.get_formview_action()
        action["res_id"] = wiz.id
        return action
