# Copyright 2025 Binhex <https://www.binhex.cloud>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class QualityControlValidateWizard(models.TransientModel):
    _name = "quality.control.validate.wizard"
    _description = "Go to validate quality control"

    def action_validate_quality_control(self):
        context = dict(self.env.context)
        wizard_id = self.env[context["active_model"]].browse(context["active_id"])
        wizard_id.picking_id._action_done()
        if self.env.context.get("go_validate_quality_control", False) and wizard_id:
            return wizard_id.picking_id.action_validate_quality_control()
        return self.env["ir.actions.actions"]._for_xml_id(
            "stock_barcodes.action_stock_barcodes_action"
        )
