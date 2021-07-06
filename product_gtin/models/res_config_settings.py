# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    check_code_type_ean8 = fields.Boolean(
        string="Check code type Ean8",
        related="company_id.check_code_type_ean8",
        readonly=False,
    )
    check_code_type_isbn10 = fields.Boolean(
        string="Check code type Isbn10",
        related="company_id.check_code_type_isbn10",
        readonly=False,
    )
    check_code_type_upc = fields.Boolean(
        string="Check code type Upc",
        related="company_id.check_code_type_upc",
        readonly=False,
    )
    check_code_type_ean13 = fields.Boolean(
        string="Check code type Ean13",
        related="company_id.check_code_type_ean13",
        readonly=False,
    )
