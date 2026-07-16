# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):

    _inherit = "res.company"

    enforce_gtin_barcodes = fields.Boolean(
        string="Enforce GTIN Barcodes",
        default=False,
        help="Enforce that all product barcodes follow GTIN rules.",
    )
