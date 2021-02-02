# Copyright 2021 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class BarcodeRuleUserFake(models.Model):
    _inherit = "barcode.rule"

    generate_model = fields.Selection(selection_add=[("res.users", "Users")])

    type = fields.Selection(selection_add=[("user", "User")])


class BarcodeGeneratorUserFake(models.Model):
    _name = "res.users"
    _inherit = ["res.users", "barcode.generate.mixin"]

    barcode = fields.Char("Barcode", copy=False)
