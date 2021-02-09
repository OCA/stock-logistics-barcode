# Copyright 2019 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class StockBarcodesReadLog(models.Model):
    _inherit = "stock.barcodes.read.log"

    secondary_uom_id = fields.Many2one(
        comodel_name="product.secondary.unit", string="Secondary uom",
    )
    secondary_uom_qty = fields.Float(
        string="Secondary UOM Qty", digits="Product Unit of Measure"
    )
