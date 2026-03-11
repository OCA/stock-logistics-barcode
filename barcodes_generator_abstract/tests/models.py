# Copyright 2021 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models

# pylint: disable=consider-merging-classes-inherited


class BarcodeRuleUserFake(models.Model):
    _inherit = "barcode.rule"

    generate_model = fields.Selection(
        selection_add=[("res.users.tester", "Users")],
        ondelete={"res.users.tester": "cascade"},
    )

    type = fields.Selection(
        selection_add=[("user", "User")], ondelete={"user": "cascade"}
    )


class BarcodeGeneratorUserFake(models.Model):
    _name = "res.users.tester"
    _description = "Res Users Tester"
    _inherit = ["res.users", "barcode.generate.mixin"]

    barcode = fields.Char(copy=False)
    company_ids = fields.Many2many(relation="res_users_tester_company_rel")
    group_ids = fields.Many2many(relation="res_users_tester_groups_rel")
    role_ids = fields.Many2many(relation="res_users_tester_roles_rel")

    def init(self):
        """This is just to avoid errors during test model registry
        because auth_totp launches a script about totp_secret column"""
        pass
