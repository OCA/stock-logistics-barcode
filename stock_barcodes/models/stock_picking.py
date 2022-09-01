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
            "manual_entry": option_group.manual_entry,
            "picking_mode": "picking",
        }
        if self.picking_type_id.code == "outgoing":
            vals["location_dest_id"] = self.location_dest_id.id
        if self.picking_type_id.code == "incoming":
            vals["location_id"] = self.location_id.id

        if option_group.get_option_value("location_id", "filled_default"):
            vals["location_id"] = self.location_id.id
        if option_group.get_option_value("location_dest_id", "filled_default"):
            vals["location_dest_id"] = self.location_dest_id.id
        wiz = self.env["wiz.stock.barcodes.read.picking"].create(vals)
        wiz.determine_todo_action()
        wiz.fill_pending_moves()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "stock_barcodes.action_stock_barcodes_read_picking"
        )
        action["res_id"] = wiz.id
        return action

    def button_validate(self):
        if (
            self.picking_type_id.barcode_option_group_id.auto_put_in_pack
            and not self.move_line_ids.mapped("result_package_id")
        ):
            self.put_in_pack()
        return super().button_validate()
