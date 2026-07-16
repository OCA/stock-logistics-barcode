# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):

    _inherit = "res.config.settings"

    enforce_gtin_barcodes = fields.Boolean(
        related="company_id.enforce_gtin_barcodes",
        readonly=False,
    )
