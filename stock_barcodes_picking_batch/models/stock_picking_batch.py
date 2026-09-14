# Copyright 2019 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models


class StockPickingBatch(models.Model):
    _inherit = "stock.picking.batch"

    def _prepare_barcode_wiz_vals(self):
        first_picking = self.picking_ids[:1]
        option_group = (
            first_picking.picking_type_id.barcode_option_group_id
            or self.env.ref("stock_barcodes.stock_barcodes_option_group_operation")
        )
        vals = first_picking._prepare_barcode_wiz_vals(option_group)
        vals.pop("picking_id", None)
        vals.update(
            {
                "picking_batch_id": self.id,
                "res_model_id": self.env.ref(
                    "stock_picking_batch.model_stock_picking_batch"
                ).id,
                "res_id": self.id,
                "picking_mode": "picking_batch",
            }
        )
        return vals

    def action_barcode_scan(self, wiz=False):
        if not wiz:
            vals = self._prepare_barcode_wiz_vals()
            wiz = self.env["wiz.stock.barcodes.read.picking"].create(vals)
        wiz.fill_pending_moves()
        wiz.determine_todo_action()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "stock_barcodes_picking_batch.action_stock_barcodes_read_picking_batch"
        )
        action["res_id"] = wiz.id
        return action
