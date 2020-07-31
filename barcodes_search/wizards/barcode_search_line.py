# coding: utf-8
# Copyright (C) 2017-Today GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import ast
from odoo import _, api, fields, models


class BarcodeSearchLine(models.TransientModel):
    _name = "barcode.search.line"
    _description = "Barcode Search Line"

    barcode_search_id = fields.Many2one(comodel_name="barcode.search")

    model_id = fields.Many2one(
        comodel_name="ir.model",
        readonly=True,
        related="field_id.model_id",
    )

    field_id = fields.Many2one(
        string="Field",
        comodel_name="ir.model.fields",
        readonly=True,
    )

    item_ref = fields.Integer(string="Item ID", readonly=True)

    item_name = fields.Char(string="Item Name", readonly=True)

    extra_data = fields.Char()

    extra_data_display = fields.Text(
        string="Extra Data",
        compute="_compute_extra_data_display",
    )

    @api.depends("extra_data")
    def _compute_extra_data_display(self):
        for line in self:
            res = []
            for k, v in ast.literal_eval(line.extra_data).items():
                if k == "type":
                    res.append("- %s: %s" % (_("Type"), v))
                elif k == "value":
                    res.append("- %s: %s" % (_("Value"), v))
            line.extra_data_display = "\n".join(res)

    @api.multi
    def button_view(self):
        self.ensure_one()
        CurrentModel = self.env[self.model_id.model]
        record = CurrentModel.browse(self.item_ref)
        return record.get_formview_action()
