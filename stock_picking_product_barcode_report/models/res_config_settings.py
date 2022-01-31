# Copyright 2021 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    barcode_default_format = fields.Selection(
        string="Method to choose the barcode formating",
        related="company_id.barcode_default_format",
        readonly=False,
    )
    barcode_default_report = fields.Many2one(
        comodel_name="ir.actions.report",
        related="company_id.barcode_default_report",
        string="Default template for barcode labels",
        readonly=False,
    )
