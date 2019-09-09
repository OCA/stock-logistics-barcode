# Copyright 2019 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models
from odoo.addons import decimal_precision as dp


class StockBarcodesReadLog(models.Model):
    _name = 'stock.barcodes.read.log'
    _description = 'Log barcode scanner'
    _order = 'id DESC'

    name = fields.Char(string='barcode')
    res_model_id = fields.Many2one(
        comodel_name='ir.model',
        index=True,
    )
    res_id = fields.Integer(index=True)
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product',
        index=True,
    )
    lot_id = fields.Many2one(
        comodel_name='stock.production.lot',
        string='Lot scanned',
    )
    location_id = fields.Many2one(
        comodel_name='stock.location',
        string='Location',
    )
    packaging_id = fields.Many2one(
        comodel_name='product.packaging',
        string='Packaging',
    )
    packaging_qty = fields.Float(
        string='Package Qty',
        digits=dp.get_precision('Product Unit of Measure'),
    )
    product_qty = fields.Float(
        string='Quantity',
        digits=dp.get_precision('Product Unit of Measure'),
    )
    manual_entry = fields.Boolean(
        string='Manual entry',
    )
    picking_id = fields.Many2one(
        comodel_name='stock.picking',
        string='Picking',
    )
