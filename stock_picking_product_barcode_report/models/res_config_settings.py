# Copyright 2020 Carlos Roca <carlos.roca@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    barcode_default_format = fields.Selection(
        [("gs1_128", "Display GS1_128 format for barcodes")],
        string="Method to choose the barcode formating",
        related="company_id.barcode_default_format",
        readonly=False,
    )


class Company(models.Model):
    _inherit = "res.company"

    barcode_default_format = fields.Selection(
        [("gs1_128", "Display GS1_128 format for barcodes")],
        string="Method to choose the barcode formating",
    )
