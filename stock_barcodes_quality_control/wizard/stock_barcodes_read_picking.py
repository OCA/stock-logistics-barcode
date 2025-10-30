# Copyright 2025 Binhex <https://www.binhex.cloud>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class WizStockBarcodesReadPicking(models.TransientModel):
    _inherit = "wiz.stock.barcodes.read.picking"

    show_quantity_control = fields.Boolean(compute="_compute_show_quantity_control")
    signature = fields.Image(help="Signature", copy=False, attachment=True)
    is_enable_signature = fields.Boolean(compute="_compute_is_enable_signature")

    def _compute_is_enable_signature(self):
        for wiz in self:
            wiz.is_enable_signature = (
                self.env.user.has_group("stock.group_stock_sign_delivery")
                and wiz.picking_id.picking_type_code == "outgoing"
                and wiz.picking_id.state != "done"
            )

    @api.depends("picking_id.created_inspections")
    def _compute_show_quantity_control(self):
        for wiz in self:
            wiz.show_quantity_control = wiz.picking_id.created_inspections > 0

    def valid_show_quantity_control(self):
        picking_id = self.picking_id
        product_ids = picking_id.mapped("move_ids_without_package.product_id")
        test_ids = (
            product_ids.mapped("qc_triggers.test")
            + product_ids.mapped("product_tmpl_id.qc_triggers").mapped("test")
            + self.env["qc.inspection"]
            .search(
                [
                    "&",
                    "|",
                    ("product_id", "in", product_ids.ids),
                    ("picking_id", "=", picking_id.id),
                    ("state", "=", "ready"),
                ]
            )
            .mapped("test")
        )
        return (
            self._name == "wiz.stock.barcodes.read.picking"
            and self.option_group_id.show_quality_control
            and test_ids
            and all(val.active is True for val in test_ids)
        )

    def _action_quality_control_validate(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": "quality.control.validate.wizard",
            "view_mode": "form",
            "name": _("Quality control"),
            "target": "new",
        }

    def open_show_control_quality_control(self):
        return self.picking_id.action_validate_quality_control()

    def write(self, vals):
        if "signature" in vals:
            self.picking_id.signature = vals["signature"]
        return super().write(vals)

    def action_validate_picking(self):
        if self.valid_show_quantity_control():
            return self._action_quality_control_validate()
        return super().action_validate_picking()
