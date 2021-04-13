# Copyright 2019 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class StockBarcodesOptionGroup(models.Model):
    _name = "stock.barcodes.option.group"
    _description = "Options group for barcode interface"

    name = fields.Char()
    code = fields.Char()
    option_ids = fields.One2many(
        comodel_name="stock.barcodes.option", inverse_name="option_group_id", copy=True
    )
    barcode_guided_mode = fields.Selection(
        [("guided", "Guided")], string="Guide mode for barcode"
    )
    manual_entry = fields.Boolean(string="Manual entry data")
    confirmed_moves = fields.Boolean(string="Confirmed moves")

    def get_option_value(self, field_name, attribute):
        option = self.option_ids.filtered(
            lambda op: op.field_name == field_name
            and (not op.access_group_id or self.env.user in op.access_group_id.users)
        )[:1]
        return option[attribute]


class StockBarcodesOption(models.Model):
    _name = "stock.barcodes.option"
    _description = "Options for barcode interface"
    _order = "sequence, id"

    sequence = fields.Integer(string="Sequence", default=100)
    name = fields.Char()
    code = fields.Char()
    option_group_id = fields.Many2one(comodel_name="stock.barcodes.option.group")
    access_group_id = fields.Many2one(
        comodel_name="res.groups", string="Associated group",
    )
    # next_step_id = fields.Many2one(comodel_name="stock.barcodes.option")
    field_name = fields.Char()
    filled_default = fields.Boolean()
    forced = fields.Boolean()
    is_invisible = fields.Boolean()
    to_scan = fields.Boolean()
