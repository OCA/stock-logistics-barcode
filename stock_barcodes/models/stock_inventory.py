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
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "stock_barcodes.action_stock_barcodes_read_inventory"
        )
        action["context"] = {
            "default_location_id": self.location_ids[:1].id,
            "default_product_id": self.product_ids[:1].id,
            "default_inventory_id": self.id,
            "default_res_model_id": self.env.ref("stock.model_stock_inventory").id,
            "default_res_id": self.id,
        }
        return action
