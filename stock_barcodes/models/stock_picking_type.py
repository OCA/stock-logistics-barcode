# Copyright 2019 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    def action_barcode_scan(self):
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "stock_barcodes.action_stock_barcodes_read_picking"
        )
        action["context"] = {
            "default_res_model_id": self.env.ref("stock.model_stock_picking_type").id,
            "default_res_id": self.id,
            "default_picking_type_code": self.code,
        }
        if self.code == "incoming":
            action["context"]["default_location_id"] = self.default_location_dest_id.id
        elif self.code in ["outgoing", "internal"]:
            action["context"]["default_location_id"] = self.default_location_src_id.id
        return action
