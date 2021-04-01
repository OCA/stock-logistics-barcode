# Copyright 2019 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models
from odoo.tools.safe_eval import safe_eval


class StockBarcodesAction(models.Model):
    _name = "stock.barcodes.action"
    _description = "Actions for barcode interface"

    name = fields.Char()
    sequence = fields.Integer(string="Sequence", default=100)
    action_window_id = fields.Many2one(
        comodel_name="ir.actions.act_window", string="Action window"
    )
    context = fields.Char()

    def open_action(self):
        action = self.action_window_id.read()[0]
        ctx = self.env.context.copy()
        ctx.update(safe_eval(self.context))
        action["context"] = ctx
        return action
