# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ProductSecondaryUnit(models.Model):
    _inherit = "product.secondary.unit"

    barcode = fields.Char(
        string="Barcode",
        copy=False,
        help="International Article Number used for product identification.",
    )
