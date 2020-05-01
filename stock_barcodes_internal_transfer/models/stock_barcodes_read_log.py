# Copyright 2020 Manuel Calero - Xtendoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class StockBarcodesReadLog(models.Model):
    _inherit = 'stock.barcodes.read.log'
    _description = 'Log barcode scanner'
    _order = 'id DESC'

    location_dest_id = fields.Many2one(
        comodel_name='stock.location',
    )
