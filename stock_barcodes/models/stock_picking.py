# Copyright 2019 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def action_barcode_scan(self):
        option_group = self.picking_type_id.barcode_option_group_id
        vals = {
            "picking_id": self.id,
            "res_model_id": self.env.ref("stock.model_stock_picking").id,
            "res_id": self.id,
            "picking_type_code": self.picking_type_code,
            "option_group_id": option_group.id,
            "picking_mode": "picking",
        }
        if option_group.get_option_value("location_id", "filled_default"):
            out_picking = self.picking_type_code == "outgoing"
            location = self.location_id if out_picking else self.location_dest_id
            vals["location_id"] = location.id
        wiz = self.env["wiz.stock.barcodes.read.picking"].create(vals)
        wiz.determine_todo_action()
        action = self.env.ref(
            "stock_barcodes.action_stock_barcodes_read_picking"
        ).read()[0]
        action["res_id"] = wiz.id
        return action
