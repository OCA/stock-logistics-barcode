# Copyright 2020 Manuel Calero - Xtendoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def action_barcode_internal_transfer_scan(self):
        action = self.env.ref(
            'stock_barcodes_internal_transfer.action_stock_barcodes_read_internal_transfer').read()[0]
        action['context'] = {
            'default_location_id': self.location_id.id,
            'default_location_dest_id': self.location_dest_id.id,
            'default_partner_id': self.partner_id.id,
            'default_picking_id': self.id,
            'default_res_model_id':
                self.env.ref('stock.model_stock_picking').id,
            'default_res_id': self.id,
            'default_picking_type_code': self.picking_type_code,
        }
        return action
