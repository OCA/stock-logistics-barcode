# Copyright 2021 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    is_barcode_label = fields.Boolean(string="Barcode label")
