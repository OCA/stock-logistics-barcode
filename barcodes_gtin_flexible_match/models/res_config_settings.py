# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):

    _inherit = "res.config.settings"

    barcode_flexible_gtin_match = fields.Boolean(
        related="company_id.barcode_flexible_gtin_match",
        readonly=False,
    )
