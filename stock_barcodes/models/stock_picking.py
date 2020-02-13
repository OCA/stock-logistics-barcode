# Copyright 2019 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def action_barcode_scan(self):
        out_picking = self.picking_type_code == "outgoing"
        location = self.location_id if out_picking else self.location_dest_id
        action = self.env.ref(
            "stock_barcodes.action_stock_barcodes_read_picking"
        ).read()[0]
        action["context"] = {
            "default_location_id": location.id,
            "default_partner_id": self.partner_id.id,
            "default_picking_id": self.id,
            "default_res_model_id": self.env.ref("stock.model_stock_picking").id,
            "default_res_id": self.id,
            "default_picking_type_code": self.picking_type_code,
        }
        return action
