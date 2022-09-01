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
        option_group = self.env.ref(
            "stock_barcodes.stock_barcodes_option_group_inventory"
        )
        if option_group.auto_lot:
            # Disable lot_id step required
            option_group.option_ids.filtered(
                lambda p: p.field_name == "lot_id"
            ).required = False
        vals = {
            "inventory_id": self.id,
            "res_model_id": self.env.ref("stock.model_stock_inventory").id,
            "res_id": self.id,
            "option_group_id": self.env.ref(
                "stock_barcodes.stock_barcodes_option_group_inventory"
            ).id,
            "manual_entry": option_group.manual_entry,
        }
        if option_group.get_option_value("location_id", "filled_default"):
            vals["location_id"] = self.location_ids[:1].id
        wiz = self.env["wiz.stock.barcodes.read.inventory"].create(vals)
        action = self.env["ir.actions.actions"]._for_xml_id(
            "stock_barcodes.action_stock_barcodes_read_inventory"
        )
        action["res_id"] = wiz.id
        return action
