# Copyright 2025 Binhex <https://www.binhex.cloud>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class StockBarcodesOptionGroup(models.Model):
    _inherit = "stock.barcodes.option.group"

    show_quality_control = fields.Boolean(
        default=False,
        help="Defines whether, when validating a pick from the barcode view, "
        "notification should be given of the existence of quality"
        " checks and whether they should be carried out at the time.",
    )
