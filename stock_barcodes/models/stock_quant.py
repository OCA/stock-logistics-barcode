# Copyright 2023 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models

MODEL_UPDATE_INVENTORY = ["wiz.stock.barcodes.read.inventory"]


class StockQuant(models.Model):
    _name = "stock.quant"
    _inherit = ["stock.quant", "barcodes.barcode_events_mixin"]

    def action_barcode_inventory_quant_unlink(self):
        self.with_context(inventory_mode=True).action_set_inventory_quantity_to_zero()
        context = dict(self.env.context)
        params = context.get("params", {})
        res_model = params.get("model", False)
        res_id = params.get("id", False)
        if res_id and res_model in MODEL_UPDATE_INVENTORY:
            wiz_id = self.env[params["model"]].browse(params["id"])
            wiz_id._compute_count_inventory_quants()
            wiz_id.send_bus_done(
                "stock_barcodes_form_update",
                "count_apply_inventory",
                {"count": wiz_id.count_inventory_quants},
            )

    def _get_fields_to_edit(self):
        return [
            "location_id",
            "product_id",
            "product_uom_id",
            "lot_id",
            "package_id",
        ]

    def action_barcode_inventory_quant_edit(self):
        wiz_barcode_id = self.env.context.get("wiz_barcode_id", False)
        wiz_barcode = self.env["wiz.stock.barcodes.read.inventory"].browse(
            wiz_barcode_id
        )
        for quant in self:
            # Try to assign fields with the same name between quant and the scan wizard
            for fname in self._get_fields_to_edit():
                wiz_barcode[fname] = quant[fname]
            wiz_barcode.product_qty = quant.inventory_quantity

        wiz_barcode.manual_entry = True
        self.send_bus_done(
            "stock_barcodes_scan",
            "stock_barcodes_edit_manual",
            {
                "manual_entry": True,
            },
        )

    def enable_current_operations(self):
        self.send_bus_done(
            "stock_barcodes_kanban_update",
            "enable_operations",
            {
                "id": self.id,
            },
        )

    def operation_quantities_rest(self):
        self.write({"inventory_quantity": self.inventory_quantity - 1})
        self.enable_current_operations()

    def operation_quantities(self):
        self.write({"inventory_quantity": self.inventory_quantity + 1})
        self.enable_current_operations()

    def action_apply_inventory(self):
        res = super().action_apply_inventory()
        self.send_bus_done(
            "stock_barcodes_scan",
            "actions_barcode",
            {"apply_inventory": True},
        )
        return res
