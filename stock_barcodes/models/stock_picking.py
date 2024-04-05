# Copyright 2019 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models
from odoo.tools.float_utils import float_compare


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _prepare_barcode_wiz_vals(self, option_group):
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
        return vals

    def action_barcode_scan(self, option_group=False):
        option_group = option_group or self.picking_type_id.barcode_option_group_id
        wiz = self.env["wiz.stock.barcodes.read.picking"].create(
            self._prepare_barcode_wiz_vals(option_group)
        )
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
            self.action_put_in_pack()
        create_backorder = False
        # Variable initialized as True to optimize break loop
        skip_backorder = True
        if self.env.context.get("stock_barcodes_validate_picking", False):
            # Avoid backorder when all move lines are processed (done or done_forced)
            prec = self.env["decimal.precision"].precision_get(
                "Product Unit of Measure"
            )
            for move in self.move_ids.filtered(lambda sm: sm.state != "cancel"):
                if (
                    float_compare(
                        move.quantity_done, move.product_uom_qty, precision_digits=prec
                    )
                    < 0
                ):
                    # In normal conditions backorder will be created
                    create_backorder = True
                    if not move.move_line_ids or any(
                        sml.state in ["pending"] for sml in move.move_line_ids
                    ):
                        # If any move are not processed we can not skip backorder
                        skip_backorder = False
                        break
        if create_backorder and skip_backorder:
            res = super(
                StockPicking,
                self.with_context(
                    picking_ids_not_to_backorder=self.ids, skip_backorder=True
                ),
            ).button_validate()
        else:
            res = super().button_validate()
        if res is True and self.env.context.get("show_picking_type_action_tree", False):
            return self[:1].picking_type_id.get_action_picking_tree_ready()
        return res
