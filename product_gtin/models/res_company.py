# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    check_code_type_ean8 = fields.Boolean()
    check_code_type_isbn10 = fields.Boolean()
    check_code_type_upc = fields.Boolean()
    check_code_type_ean13 = fields.Boolean()
