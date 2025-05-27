# Copyright 2025 Binhex <https://www.binhex.cloud>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def action_validate_quality_control(self):
        context = dict(self.env.context)
        domain = [
            ("picking_id", "=", self.id),
        ]
        context.update({"create": False})
        action = self.env["ir.actions.actions"]._for_xml_id(
            "quality_control_oca.action_qc_inspection"
        )
        action["domain"] = domain
        return action

    def get_count_sign_delivery_slip(self):
        filename = "%s_signed_delivery_slip.pdf" % self.name
        return self.env["ir.attachment"].search_count(
            [
                ("res_model", "=", self._name),
                ("res_id", "=", self.id),
                ("name", "=", filename),
            ]
        )
