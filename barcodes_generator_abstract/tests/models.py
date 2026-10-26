# Copyright 2021 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models

# pylint: disable=consider-merging-classes-inherited


class BarcodeRuleUserFake(models.Model):
    _inherit = "barcode.rule"

    generate_model = fields.Selection(
        selection_add=[("barcode.generate.tester", "Tester")],
        ondelete={"barcode.generate.tester": "cascade"},
    )

    type = fields.Selection(
        selection_add=[("user", "User")], ondelete={"user": "cascade"}
    )


class BarcodeGeneratorUserFake(models.Model):
    _name = "barcode.generate.tester"
    _description = "Barcode Generate Tester"
    _inherit = "barcode.generate.mixin"

    name = fields.Char()
    barcode = fields.Char(copy=False)
