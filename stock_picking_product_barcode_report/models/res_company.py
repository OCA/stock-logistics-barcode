# Copyright 2021 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class Company(models.Model):
    _inherit = "res.company"

    barcode_default_format = fields.Selection(
        [("gs1_128", "Display GS1_128 format for barcodes")],
        string="Method to choose the barcode formating",
    )
    barcode_default_report = fields.Many2one(
        comodel_name="ir.actions.report",
        string="Default template for barcode labels",
        domain=[("is_barcode_label", "=", True)],
    )
