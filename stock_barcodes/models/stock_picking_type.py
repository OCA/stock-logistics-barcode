# Copyright 2019 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    barcode_option_group_id = fields.Many2one(
        comodel_name="stock.barcodes.option.group"
    )

    def action_barcode_scan(self):
        action = self.env.ref(
            "stock_barcodes.action_stock_barcodes_read_picking"
        ).read()[0]
        action["context"] = {
            "default_res_model_id": self.env.ref("stock.model_stock_picking_type").id,
            "default_res_id": self.id,
            "default_picking_type_code": self.code,
            "guided_mode": self.barcode_option_group_id.barcode_guided_mode,
            "control_panel_hidden": True,
            "picking_mode": "picking",
            "default_option_group_id": self.barcode_option_group_id.id,
        }
        if self.barcode_option_group_id.get_option_value(
            "location_id", "filled_default"
        ):
            if self.code == "incoming":
                location = self.default_location_dest_id
            elif self.code in ["outgoing", "internal"]:
                location = self.default_location_src_id
            action["context"]["default_location_id"] = location.id
        return action
