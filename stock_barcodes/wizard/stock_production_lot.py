# Copyright 2019 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class WizStockBarcodesNewLot(models.TransientModel):
    _inherit = 'barcodes.barcode_events_mixin'
    _name = 'wiz.stock.barcodes.new.lot'
    _description = 'Wizard to create new lot from barcode scanner'

    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product',
        required=True,
    )
    lot_name = fields.Char(
        string='Lot name',
        required=True,
    )

    def clean_values(self):
        self.product_id = False
        self.lot_name = False

    def on_barcode_scanned(self, barcode):
        product = self.env['product.product'].search([
            ('barcode', '=', barcode),
        ])[:1]
        if product and not self.product_id:
            self.product_id = product
            return
        self.lot_name = barcode

    def _prepare_lot_values(self):
        return {
            'product_id': self.product_id.id,
            'name': self.lot_name,
        }

    def confirm(self):
        return self.env['stock.production.lot'].create(
            self._prepare_lot_values())
