# Copyright 2021 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    stock_barcodes_auto_lot = fields.Boolean(
        string='Get lots automatically',
        related="company_id.stock_barcodes_auto_lot",
        readonly=False,
    )
    group_track_pending_products_picking_barcode_wizard = fields.Boolean(
        string="Track pending products at the picking barcode wizard",
        implied_group="stock_barcodes."
                      "group_track_pending_products_picking_barcode",
    )


class ResCompany(models.Model):
    _inherit = "res.company"

    stock_barcodes_auto_lot = fields.Boolean()
