# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    barcode_flexible_gtin_match = fields.Boolean(
        string="Flexible GTIN Barcode Matching",
        default=False,
        help="When enabled, barcode lookups will match GTIN variants "
        "(GTIN-8, GTIN-12, GTIN-13, GTIN-14) regardless of leading zeros.",
    )
