# Copyright 2021 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    stock_barcodes_inventory_auto_lot = fields.Boolean(
        string="Get lots automatically for inventories",
        related="company_id.stock_barcodes_inventory_auto_lot",
        readonly=False,
    )


class ResCompany(models.Model):
    _inherit = "res.company"

    stock_barcodes_inventory_auto_lot = fields.Boolean()
