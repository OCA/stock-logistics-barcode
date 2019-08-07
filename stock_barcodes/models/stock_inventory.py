# Copyright 2019 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models


class StockInventory(models.Model):
    _inherit = ['barcodes.barcode_events_mixin', 'stock.inventory']
    _name = 'stock.inventory'

    def action_barcode_scan(self):
        action = self.env.ref(
            'stock_barcodes.action_stock_barcodes_read_inventory').read()[0]
        action['context'] = {
            'default_location_id': self.location_id.id,
            'default_product_id': self.product_id.id,
            'default_prod_lot_id': self.lot_id.id,
            'default_package_id': self.package_id.id,
            'default_partner_id': self.partner_id.id,
            'default_inventory_id': self.id,
            'default_res_model_id':
                self.env.ref('stock.model_stock_inventory').id,
            'default_res_id': self.id,
        }
        return action
