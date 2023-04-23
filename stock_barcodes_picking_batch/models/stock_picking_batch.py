# Copyright 2019 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models


class StockPickingBatch(models.Model):
    _inherit = "stock.picking.batch"

    def action_barcode_scan(self):
        first_picking = self.picking_ids[:1]
        picking_type_code = first_picking.picking_type_code
        option_group = first_picking.picking_type_id.barcode_option_group_id
        vals = {
            "picking_batch_id": self.id,
            "res_model_id": self.env.ref(
                "stock_picking_batch.model_stock_picking_batch"
            ).id,
            "res_id": self.id,
            "picking_type_code": picking_type_code,
            "option_group_id": option_group.id,
            "picking_mode": "picking_batch",
        }
        if first_picking.picking_type_id.code == "outgoing":
            vals["location_dest_id"] = first_picking.location_dest_id.id
        if first_picking.picking_type_id.code == "incoming":
            vals["location_id"] = first_picking.location_id.id

        if option_group.get_option_value("location_id", "filled_default"):
            vals["location_id"] = first_picking.location_id.id
        if option_group.get_option_value("location_dest_id", "filled_default"):
            vals["location_dest_id"] = first_picking.location_dest_id.id
        wiz = self.env["wiz.stock.barcodes.read.picking"].create(vals)
        wiz.determine_todo_action()
        wiz.fill_pending_moves()
        action = self.env.ref(
            "stock_barcodes_picking_batch.action_stock_barcodes_read_picking_batch"
        ).read()[0]
        action["res_id"] = wiz.id
        return action
