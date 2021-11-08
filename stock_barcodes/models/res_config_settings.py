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
    group_picking_barcode_wizard_non_detailed_operations = fields.Boolean(
        string="Show non-detailed operations",
        implied_group="stock_barcodes."
        "group_track_pending_products_picking_barcode_non_detailed_operations",
    )
    group_picking_barcode_wizard_detailed_operations = fields.Boolean(
        string="Show detailed operations",
        implied_group="stock_barcodes."
        "group_track_pending_products_picking_barcode_detailed_operations",
    )


class ResCompany(models.Model):
    _inherit = "res.company"

    stock_barcodes_inventory_auto_lot = fields.Boolean()
